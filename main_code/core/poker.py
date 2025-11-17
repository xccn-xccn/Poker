import random
from collections import defaultdict
from copy import deepcopy
from abc import ABC
from core.winner import get_winner, all_hands_ranked, group_rank_pre
from core.backbone_misc import *


# TODO test valid bets on raises
# TODO show hands if only one player left
# TODO make calling range capped and raising range tighter with percentages
# TODO Consider hand within all hands (not just range)
# TODO test get_ps_strength
# BUG main player could do an uneccessary fold and make chips disappear
# TODO bots dont bet thinly enough post flop
# TODO consider draws
# TODO tighten opening range
# TODO change range depending on position and num of players
# TODO hold invested of each player? currently inefficient replace the functions
# TODO if big bet and 1 player calls, bb will also call with nothing
# TODO consider hand strength with betsize
# TODO should end when folds to bb
# TODO BOT v1 is very bad heads up (worse than random)
# 3bet more oop
# underbluffs?
# Use mdf or pot odds


class PokerPlayer(ABC):
    pos_i_names = {
        0: "Button",
        1: "Small blind",
        2: "Big blind",
        3: "UTG",
        4: "Hijack",
        5: "Cutoff",
    }

    def __init__(self, table, id=0, chips=1000):
        self.chips = chips
        self.table = table
        self.id = id
        self.round_invested = 0
        self.inactive = False
        self.action = None
        self.hole_cards = None
        self.position_name = None
        self.fold = True

        while self.id == 0 or self.id in table.ids:
            self.id = random.randint(1000, 9999)

    def __eq__(self, other):
        if not isinstance(other, PokerPlayer):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def set_pos_names(self, players):
        self.pos_names = {}
        for i, pos in enumerate(
            [
                *[
                    "UTG" + (f" +{n}" if n != 0 else "")
                    for n in range(max(players - 5, 0))
                ],
                "Lojack",
                "Hijack",
                "Cutoff",
                "Button",
                "Small blind",
                "Big blind",
            ][-players:]
        ):
            self.pos_names[i + 1] = pos

    def new_hand(self, i):

        self.fold = False
        self.agg = False
        if self.chips <= 0:
            self.fold = True

        a_player_count = len(self.table.active_players)
        self.position_i = ((i - self.table.sb_i) % a_player_count + 1) % a_player_count
        self.position_name = PokerPlayer.pos_i_names[self.position_i]
        self.hole_cards = self.table.deck[self.position_i * 2 : self.position_i * 2 + 2]

        if a_player_count == 2:  # heads up
            self.total_invested = min(self.table.blinds[self.position_i], self.chips)
        elif self.position_i in [1, 2]:  # One of the blinds maybe change to name
            self.total_invested = min(
                self.table.blinds[self.position_i - 1], self.chips
            )
        else:
            self.total_invested = 0

        self.round_invested = self.extra = self.total_invested
        self.chips -= self.round_invested
        self.all_in = not (bool(self.chips) or self.fold)

    def end_round(self, start=False):
        if not start:
            # for the blinds
            self.round_invested = 0
        self.action = self.action_text = None
        self.extra = 0
        self.only_call = False

    def move_action(self, roundTotal):
        if self.action == 1:
            # self.action_text is only for debugging
            self.action_text = "folds"
            self.fold = True
            self.agg = False
            self.extra = 0

        elif self.action == 2:

            self.agg = False
            self.extra = roundTotal - self.round_invested
            self.action_text = "calls" if self.extra else "checks"

            if roundTotal >= self.round_invested + self.chips:
                self.all_in = True
                self.extra = self.chips

        else:
            self.action_text = f"bets {self.extra}"

            self.agg = True

            self.only_call = (
                self.round_invested + self.extra
                < self.table.last_bet + self.table.min_raise
            )

        self.round_invested += self.extra
        self.total_invested += self.extra
        self.chips -= self.extra

        if self.chips == 0:
            self.all_in = True

    def is_valid(self, table, action_info):
        print(action_info)
        action, extra = action_info[0], action_info[1] - self.round_invested  # CHANGE

        if isinstance(self, Human):
            if table.community:
                end = f", Community Cards {table.community}"
            else:
                end = ""

            print(f"\n Your cards are {self.hole_cards}{end}")
        else:
            print(f"\n {self.position_name} cards are {self.hole_cards}")

        if action == 3:
            print(
                self.round_invested,
                action_info,
                table.last_bet,
                table.min_raise,
                self.chips,
            )

            if (
                (
                    self.round_invested + extra < table.last_bet + table.min_raise
                    and extra < self.chips
                )
                or extra > self.chips
                or table.only_call == True
                or self.round_invested + extra < table.last_bet
            ):
                print("invalid")
                return False

        return True

    def move(self, table, action_info):

        valid = self.is_valid(table, action_info)

        if not valid and isinstance(self, Bot):
            print(
                table.last_bet,
                action_info,
                self.round_invested,
                self.chips,
                self.can_only_call(),
                self.table.r,
            )
            raise Exception
        elif not valid:
            return False

        # self.action, self.extra = action_info #CHANGE
        self.action, self.extra = (
            action_info[0],
            action_info[1] - self.round_invested,
        )  # CHANGE
        self.move_action(table.last_bet)

        # TODO
        name = "(YOU)" if isinstance(self, Human) else "(BOT)"
        print(
            f"\n {self.position_name} {name} {self.action_text} with {self.chips} chips behind {self.round_invested} invested this round"
        )

        return True

    def add_chips(self, extra):
        self.chips += extra

    def get_pot(
        self,
    ):
        count = 0
        pot_sum = 0
        for p in self.table.pot:
            count += p[0]
            if count > self.chips + self.total_invested:
                rem_chips = self.chips + self.total_invested - count + p[0]
                pot_sum += sum([min(rem_chips, x) for x in p[2].values()])
                return pot_sum
            pot_sum += sum(p[2].values())
        return pot_sum

    def get_round_total(self):
        return min(self.table.last_bet, self.chips + self.round_invested)


class Bot(PokerPlayer):
    def can_only_call(self):
        return (
            self.table.last_bet >= self.round_invested + self.chips
            or self.table.only_call == True
        )


class RandomBot(Bot):
    def get_bet(self, table):
        print("bets", table.last_bet)

        try:
            extra = random.randint(
                min(
                    self.chips + self.round_invested, table.last_bet + table.min_raise
                ),  # changed
                min(
                    max(
                        table.last_bet * 2 + table.min_raise,
                        int(table.get_pot() * 2.5),
                    ),
                    self.chips + self.round_invested,
                ),
            )

            if extra < 0:
                raise Exception

        except:
            print("ERROR", self.chips, self.round_invested, table.last_bet, table.pot)
            print(
                min(self.chips, table.last_bet - self.round_invested + table.last_bet),
                min(int(table.get_pot() * 2.5), self.chips),
            )
            raise Exception

        return extra

    def get_action(self, table):

        round_total = table.last_bet
        l = 1
        h = 3
        if round_total == self.round_invested:
            l = 2
        if self.can_only_call():
            h = 2

        action = random.randint(l, h)

        if action == 3:
            bet = self.get_bet(table)
        else:
            bet = 0

        # return 2, 0
        # return 3, self.chips
        return action, bet


class BotV1(Bot):
    def __init__(self, table, id=0, chips=1000):
        super().__init__(table, id=id, chips=chips)
        self.MDFC = 1
        self.RMDFC = 1.3

    def new_hand(self, i):
        self.c_range = None
        return super().new_hand(i)

    def pre_flop_bet(self, table):
        if table.to_bb(table.last_bet) <= 3 or table.still_to_act == 0:
            print("in bb", table.to_bb(table.last_bet))

            return (
                table.last_bet * 3
                + sum(
                    table.blinds[-1]
                    for p in table.active_players
                    if p.round_invested == 20
                )
                - table.blinds[-1]
            )  # for bb

        return table.last_bet * 2

    def get_bet(self, table):
        print("bets", table.last_bet)

        if table.r == 0:
            return min(
                self.pre_flop_bet(table), self.chips + self.round_invested
            )  # changed
        try:
            extra = random.randint(
                min(
                    self.chips + self.round_invested, table.last_bet + table.min_raise
                ),  # changed
                min(
                    max(
                        table.last_bet * 2 + table.min_raise,
                        int(table.get_pot() * 2.5),
                    ),
                    self.chips + self.round_invested,
                ),
            )

            if extra < 0:
                raise Exception

        except:
            print("ERROR", self.chips, self.round_invested, table.last_bet, table.pot)
            print(
                min(self.chips, table.last_bet - self.round_invested + table.last_bet),
                min(int(table.get_pot() * 2.5), self.chips),
            )
            raise Exception

        return extra

    def pre_flop(self, table):

        self.set_pre_var(table)

        r = random.randint(1, 10)

        print(
            "max_chips",
            self.round_total,
            self.max_chips,
            self.min_call,
            self.max_call,
            # pot_odds,
            self.to_call,
            table.cPI == table.last_agg,
            (table.cPI + 1) % table.no_players,
            table.last_agg,
            r,
            table.still_to_act(),
            table.last_bet,
            self.get_pot(),
        )

        if self.max_call != True and (
            (self.round_total < self.max_chips / 2 and r >= 2)
            or (self.min_call and (r >= 10 or table.last_bet == 20))
        ):
            return 3, self.get_bet(table)
        elif self.min_call:
            return 2, 0
        return 1, 0

    def valid_pre_po(self):
        return self.pot_odds > 3 and self.table.still_to_act() == 0

    def set_pre_var(self, table):
        self.round_total = self.get_round_total()
        self.pot_odds = self.calc_po(frac=True)

        c1, c2 = self.hole_cards

        i1, i2 = strength_index(c1, c2)

        strength = strengths[i1][i2]
        self.max_chips = strength**3 * 3 * table.blinds[-1]
        self.min_call = self.round_total < self.max_chips
        self.max_call = False
        if self.min_call == False and (self.to_call == 0 or self.valid_pre_po()):
            self.min_call = self.max_call = True
        self.max_call = self.max_call or self.can_only_call()

    def fsp_range(self, hands=None, min_strength=-1, max_strength=float("inf")):

        if hands == None:
            hands = sorted_hands
        self.c_range = group_rank_pre(
            sorted_hands[
                strengths_to_index[get_ps_strength(max_strength, minimum=False)][
                    0
                ] : strengths_to_index[get_ps_strength(min_strength)][-1]
                + 1
            ],
        )

    def spc_range(self, flag=False):
        if self.valid_pre_po() or self.to_call == 0 and not flag:
            min_strength = 0
            if self.c_range != None:
                return
        else:
            min_strength = (self.round_total / self.table.blinds[-1] / 3) ** (1 / 3)
            # max_strength = (self.round_total * 2 / self.table.blinds[-1] / 3) ** (1 / 3)

        self.fsp_range(min_strength=min_strength)

    def spr_range(self):  # TODO
        if self.table.last_bet == 20:
            self.spc_range(flag=True)
        else:
            min_strength = (self.round_total * 2 / self.table.blinds[-1] / 3) ** (1 / 3)

            self.fsp_range(min_strength=min_strength)

    def sp_range(self, action):
        if action == 1:
            self.c_range = None
            return
        flag = action == 3
        self.spc_range(flag)

    def post_flop(self, table):

        self.c_range = all_hands_ranked(table.community, p_hands=self.c_range.keys())
        min_rank = len(self.c_range) * self.calc_mdf()

        try:
            rank = self.c_range[sort_hole(*self.hole_cards)]
        except:
            print(self.c_range)
            rank = self.c_range[sort_hole(*self.hole_cards)]
            raise Exception

        action = None
        if rank > min_rank and self.to_call > 0:
            return (1, 0)
        elif self.can_only_call() or rank > min_rank / 3:
            action = (2, 0)
        else:
            action = (3, self.get_bet(table))

            min_rank *= (
                self.calc_mdf(applied=False, bet=action[1] - table.last_bet)
                * self.RMDFC
            )

            print(self.calc_mdf(applied=False, bet=action[1] - table.last_bet))

        self.c_range = all_hands_ranked(
            table.community,
            p_hands=[h for h, r in self.c_range.items() if r <= min_rank],
        )

        print(rank, len(self.c_range), action)

        if rank > len(self.c_range):
            self.c_range[sort_hole(*self.hole_cards)] = (
                len(self.c_range) + 1
            )  # uneeded?
        return action

    def get_action(self, table):
        self.to_call = min(
            table.last_bet - self.round_invested, self.chips
        )  # make function

        if table.r == 0:
            action = self.pre_flop(table)
            self.sp_range(action)
        else:
            action = self.post_flop(table)

        # return 2, 0
        return action

    def calc_mdf(self, applied=True, bet=None):
        return (
            (self.get_pot() - self.to_call) / self.get_pot()
            if applied
            else self.get_pot() / (self.get_pot() + bet)
        )

    def calc_po(self, frac=False):
        """Calculate pot odds"""
        po = (self.to_call) / (self.get_pot() + self.to_call)
        return po if frac == False else po**-1 if po != 0 else float("inf")


class Human(PokerPlayer):
    pass


class Table:
    # deck = ['🂱', '🂲', '🂳', '🂴', '🂵', '🂶', '🂷', '🂸', '🂹', '🂺', '🂻', '🂼', '🂽', '🂾', '🂡', '🂢', '��', '🂤', '🂥', '🂦', '🂧', '🂨', '🂩', '🂪', '🂫', '🂬', '🂭', '🂮', '🃁', '🃂', '🃃', '🃄', '🃅', '🃆', '🃇', '🃈', '🃉', '🃊', '🃋', '🃌', '🃍','🃑', '🃒', '🃓', '🃔', '🃕', '🃖', '🃗', '🃘', '🃙', '🃚', '🃛', '🃜', '🃝', '🃞']

    def __init__(self) -> None:
        self.players = [None] * 6
        self.active_players = []
        self.deck = deck
        self.blinds = [10, 20]
        self.sb_i = 0
        self.running = False
        self.community = []
        self.correct_total_chips = 0
        self.r = 0
        self.ids = []

    def add_new_player(self, chips=2001):
        return self.add_player(Human(self, chips=chips))

    def add_player(self, new_player: PokerPlayer) -> int | None:
        if None not in self.players:
            return

        for i, p in enumerate(self.players):
            if p == None:
                self.players[i] = new_player
                break

        self.ids.append(new_player.id)

        self.correct_total_chips += new_player.chips

        print("Added Player")
        return i

    def remove_player(self, i: int):
        pass

    def can_move(self):
        """Returns if the current player can make a move"""
        return (
            self.current_player.all_in == False
            and self.current_player.fold == False
            and self.r < self.skip_round
        )

    def next_player(self, c=None):
        if c == None:
            c = self.cPI
        return (c + 1) % self.no_players

    def validate_move(self, player_id, action_info):
        if player_id != self.current_player.id:
            return False

        return self.current_player.is_valid(self, action_info)

    def single_move(self, action_info):
        """Returns None if the move was invalid else True if the round ends else False.

        Calls and returns Table.end_move()"""
        print("player remaining", self.players_remaining)

        valid = self.current_player.move(self, action_info)

        if not valid:  # TODO decide if to return something better
            print("not valid", action_info)
            return

        if self.current_player.fold == True:
            self.players_remaining -= 1

        if self.current_player.fold or self.current_player.all_in:
            self.active_in_hand -= 1

            if self.active_in_hand == 1:
                self.skip_round = self.r + 1

        print("pre", self.pot, "\n")
        self.set_pot()
        print("pot", self.pot)
        return self.end_move()

    def end_move(self):
        """Returns True if a betting round has finished else False"""
        if self.players_remaining == 1:
            self.end_hand()
            return False

        if self.current_player.agg:
            self.last_agg = self.cPI
            self.min_raise = self.current_player.round_invested - self.last_bet
            self.last_bet = self.current_player.round_invested
            self.only_call = self.current_player.only_call

        if self.current_player.action == 3:
            self.bet_count += 1

        self.current_player.agg = False
        self.cPI = self.next_player()
        self.current_player = self.active_players[self.cPI]

        if self.current_player.agg != False:
            raise Exception(self.current_player.agg)

        self.current_player.agg = False

        if self.last_agg == self.cPI:
            return True

        return False

    def end_round(self, start=False):
        if not start:
            self.r += 1

        for p in self.active_players:
            p.end_round(start)

        if self.r == 4:
            self.end_hand()
            return

        name = {0: "Pre Flop", 1: "Flop", 2: "Turn", 3: "River"}

        self.min_raise = self.blinds[-1]
        self.only_call = False
        if self.r == 0:
            self.cPI = self.last_agg = (
                self.sb_i + (2 if self.no_players != 2 else 1)
            ) % self.no_players
            self.last_bet = self.blinds[-1]
            self.community = []
            self.bet_count = 1

        else:
            self.cPI = self.last_agg = self.sb_i
            self.last_bet = 0
            self.community = self.deck[
                self.communityCard_i : self.communityCard_i + self.r + 2
            ]
            self.bet_count = 0

            print(f"\n{name[self.r]} Cards {self.community} pot {self.pot}")

        try:
            self.current_player = self.active_players[self.cPI]
            print("b", self.r, self.current_player.position_i, self.cPI)
        except:
            print("aa", self.cPI, self.active_players, self.sb_i, self.no_players)
            raise Exception

    def set_pot(self, player=None):
        if player == None:
            player = self.current_player

        if player.fold == False:
            remaining = player.extra
            new_pot = []
            end = False

            p_before = deepcopy(self.pot)
            for p in self.pot:

                if end:
                    raise Exception(p_before, "\n", p, end)

                to_call, required, contents = p.copy()
                if remaining <= 0:  # no chips remaining (just keep it the same)
                    new_pot.append(p)
                    continue

                rem_after = remaining + contents[player] - to_call

                if rem_after < 0:  # make it subtract from the current pot
                    remaining += contents[player]
                    n_contents = defaultdict(int)
                    for k, v in contents.items():
                        n_contents[k] = min(remaining, v)
                        contents[k] = max(0, v - remaining)

                    n_contents[player] = remaining
                    new_pot.append([remaining, player.all_in, n_contents])
                    new_pot.append([to_call - remaining, required, contents])

                    remaining = 0

                elif rem_after == 0 or required:
                    contents[player] = to_call
                    new_pot.append([to_call, required or player.all_in, contents])
                    remaining = rem_after

                else:
                    if rem_after <= 0:
                        raise Exception(rem_after)
                    end = True

                    remaining = rem_after

                if remaining < 0:
                    raise Exception(self.pot, p, remaining)

            if remaining:

                if not end:
                    to_call = 0
                    contents = defaultdict(int)

                contents[player] = to_call + remaining
                new_pot.append([to_call + remaining, player.all_in, contents])

            self.pot = new_pot

    def get_pot(self):
        return sum(sum(p[2].values()) for p in self.pot)

    def next_player_i(self):
        pass

    def still_to_act(self):
        c = 0
        ci = self.next_player()
        while True:
            p = self.active_players[ci]
            if self.last_agg == ci or ci == self.cPI:
                return c
            if not (p.fold or p.all_in):
                c += 1
            ci = self.next_player(ci)

    def start_hand(self):
        self.running = True
        self.active_players = []
        button_bust = False

        for p in [x for x in self.players if x]:
            if p.chips:
                self.active_players.append(p)
                if p.inactive:
                    raise Exception(self.players, [x.chips for x in self.players])
            elif not p.inactive:
                p.inactive = True
                # p.fold = True
                if p.position_i == 0:
                    button_bust = True

        self.no_players = len(self.active_players)

        if not button_bust:
            self.sb_i = self.sb_i + 1

        self.sb_i %= self.no_players
        self.pot = [[0, False, defaultdict(int)]]
        # to_call, 1 or more players all in, each player invested in pot
        self.r = 0
        self.skip_round = float("inf")
        random.shuffle(self.deck)

        for i, p in enumerate(self.active_players):
            p.new_hand(i)

        for p in sorted(self.active_players, key=lambda x: x.total_invested)[-2:]:
            print("pre", self.pot, p.round_invested)
            self.set_pot(p)
            print("post", self.pot)

        print("pot", self.pot)

        self.active_in_hand = sum(
            [1 for p in self.active_players if not p.fold and not p.all_in]
        )
        self.players_remaining = sum([1 for p in self.active_players if not p.fold])
        self.communityCard_i = self.no_players * 2

        self.end_round(start=True)

    def give_pot(self, pot):
        c_players = [p for p, v in pot[2].items() if not p.fold and v == pot[0]]
        t_chips = sum(pot[2].values())
        if len(c_players) > 1:
            wInfo = get_winner([p.hole_cards for p in c_players], self.community)
        else:
            wInfo = [[None, 0]]

        print("winfo", wInfo)
        wHand = wInfo[0][0]
        wPIs = [x[1] for x in wInfo]
        winners = [p for i, p in enumerate(c_players) if i in wPIs]

        for i, w_p in enumerate(
            sorted(
                winners,
                key=lambda x: (x.position_i - 1) % (self.no_players + 1),
            )
        ):
            w_p.chips += t_chips // len(winners)
            if i < t_chips % len(winners):
                w_p.chips += 1
            print(w_p.chips)

        if wHand:
            end = f"with {wHand}"
        else:
            end = ""

        print([x.position_name for x in c_players])

        print(
            f"{'Winner' if len(winners) == 1 else 'Winners'} {', '.join([p.position_name for p in winners])} wins {pot} chips {end}"
        )

        print("Testing", [x.hole_cards for x in c_players], self.community)

    def end_hand(self):
        print(self.r)
        self.running = False

        for i in range(len(self.pot) - 1, -1, -1):
            print(i)
            self.give_pot(self.pot[i])

        print(
            "total_chips",
            sum(p.chips for p in self.players if p),
            len([1 for x in self.players if x and x.chips]),
        )
        if sum(p.chips for p in self.players if p) != self.correct_total_chips:
            raise Exception([p.chips for p in self.players if p])

    def to_bb(self, chips):
        return chips / self.blinds[1]


def start():
    table1 = Table()
    for r in range(5):  # CHANGE for test
        if r <= 0:
            chips = 2000
            table1.add_player(RandomBot(table1, chips=chips))

        else:
            chips = 2000
            table1.add_player(BotV1(table1, chips=chips))

    table1.add_player(
        Human(
            table1,
            chips=3000,
        )
    )
    # table1.add_player(
    #     Human(
    #         table1,
    #         chips=3000,
    #     )
    # )

    return table1


def new_table():
    pass


def main():
    table1 = start()
    running = True
    while running:
        table1.start_hand()

        input("Click Enter for next hand: \n")


if __name__ == "__main__":
    main()

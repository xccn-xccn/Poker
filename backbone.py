import random
from collections import defaultdict
from copy import deepcopy
from r_lists import deck
from winner import get_winner
from r_lists import strengths, card_values


# TODO test valid bets on raises
# TODO skip and show hands if only one player left
# TODO stop showing next round when everyone folds
# BUG main player could do an uneccessary fold and make chips disappear
# TODO make pre flop calling less loose


class Player:
    pos_i_names = {
        0: "Button",
        1: "Small blind",
        2: "Big blind",
        3: "UTG",
        4: "Hijack",
        5: "Cutoff",
    }

    def __init__(self, position_i, profile_picture, table, id, chips=1000):
        self.chips = chips
        self.position_i = self.table_position = position_i
        self.profile_picture = profile_picture
        self.inactive = False
        self.table = table
        self.id = id

    def __eq__(self, other):
        if not isinstance(other, Player):
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
        self.position_name = Player.pos_i_names[self.position_i]
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
            self.round_invested = 0
        self.action = self.action_text = None
        self.extra = 0

    def move_action(self, roundTotal):
        if self.action == 1:
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

        self.round_invested += self.extra
        self.total_invested += self.extra
        self.chips -= self.extra

        if self.chips == 0:
            self.all_in = True

    def is_valid(self, table, action):

        action, extra = action

        round_total = table.bets[-1]

        if isinstance(self, Human):
            if table.community:
                end = f", Community Cards {table.community}"
            else:
                end = ""

            print(f"\n Your cards are {self.hole_cards}{end}")
        else:
            print(f"\n {self.position_name} cards are {self.hole_cards}")

        prev_raise = table.blinds[-1]
        if len(table.bets) >= 2:
            prev_raise = table.bets[-1] - table.bets[-2]

        if action == 3:
            if (
                self.round_invested + extra < round_total + prev_raise
                and extra < self.chips
            ) or extra > self.chips:
                return False

        return True

    def move(self, table, action):

        if len(action) != 2:
            raise Exception
        valid = self.is_valid(table, action)

        if not valid and isinstance(self, Bot):
            print(table.bets, action)
            raise Exception
        elif not valid:
            return False

        self.action, self.extra = action
        self.move_action(table.bets[-1])

        name = "(YOU)" if isinstance(self, Human) else "(BOT)"
        print(
            f"\n {self.position_name} {name} {self.action_text} with {self.chips} chips behind {self.round_invested} invested this round"
        )

        return True

    def add_chips(self, extra):
        self.chips += extra


class Bot(Player):
    pass


class RandomBot(Bot):
    def get_bet(self, bets, table):
        print("bets", bets)
        prev_raise = table.blinds[-1]
        if len(bets) >= 2:
            prev_raise = bets[-1] - bets[-2]

        try:
            extra = random.randint(
                min(self.chips, bets[-1] - self.round_invested + prev_raise),
                min(
                    max(bets[-1] * 2 + prev_raise, int(table.get_total_pot() * 2.5)),
                    self.chips,
                ),
            )

            if extra < 0:
                raise Exception

        except:
            print("ERROR", self.chips, bets, self.round_invested, prev_raise, table.pot)
            print(
                min(self.chips, bets[-1] - self.round_invested + prev_raise),
                min(int(table.get_total_pot() * 2.5), self.chips),
            )
            raise Exception

        return extra

    def get_action(self, table):

        bets = table.bets
        round_total = bets[-1]
        l = 1
        h = 3
        if round_total == self.round_invested:
            l = 2
        if round_total >= self.round_invested + self.chips:
            h = 2

        action = random.randint(l, h)

        if action == 3:
            bet = self.get_bet(bets, table)
        else:
            bet = 0

        # return 2, 0
        return action, bet


class BotV1(Bot):
    def get_bet(self, bets, table):
        print("bets", bets)
        prev_raise = table.blinds[-1]
        if len(bets) >= 2:
            prev_raise = bets[-1] - bets[-2]

        try:
            extra = random.randint(
                min(self.chips, bets[-1] - self.round_invested + prev_raise),
                min(
                    max(bets[-1] * 2 + prev_raise, int(table.get_total_pot() * 2.5)),
                    self.chips,
                ),
            )

            if extra < 0:
                raise Exception

        except:
            print("ERROR", self.chips, bets, self.round_invested, prev_raise, table.pot)
            print(
                min(self.chips, bets[-1] - self.round_invested + prev_raise),
                min(int(table.get_total_pot() * 2.5), self.chips),
            )
            raise Exception

        return extra

    def pre_flop(self, table):

        round_total = table.bets[-1]
        to_call = min(round_total - self.round_invested, self.chips)
        pot_odds = float("inf") if to_call == 0 else (table.get_total_pot()) / to_call

        c1, c2 = self.hole_cards
        suited = c1[1] == c2[1]

        i1, i2 = sorted(
            (14 - card_values[c1[0]], 14 - card_values[c2[0]]), reverse=not suited
        )

        strength = strengths[i1][i2]
        max_chips = strength**3 * 3 * table.blinds[-1]
        min_call = (
            round_total < max_chips
            or to_call == 0
            or (pot_odds > 2 and table.still_to_act() == 0)
        )  # or (pot_odds >= 2 and (table.cPI + 1) % table.no_players == table.last_agg)
        r = random.randint(1, 10)

        print(
            "max_chips",
            round_total,
            max_chips,
            min_call,
            pot_odds,
            table.cPI == table.last_agg,
            (table.cPI + 1) % table.no_players,
            table.last_agg,
            r,
            table.still_to_act(),
        )

        if (round_total < max_chips / 2 and r >= 2) or (min_call and r >= 10):
            return 3
        elif min_call:
            return 2
        return 1

    def get_action(self, table):

        bets = table.bets
        round_total = bets[-1]
        l = 1
        h = 3
        if round_total == self.round_invested:
            l = 2
        if round_total >= self.round_invested + self.chips:
            h = 2

        action = random.randint(l, h)

        if table.r == 0:  # TODO bb can fold
            action = self.pre_flop(table)

        if action == 3:
            bet = self.get_bet(bets, table)
        else:
            bet = 0

        # return 2, 0
        return action, bet


class Human(Player):
    pass


class Table:
    # deck = ['🂱', '🂲', '🂳', '🂴', '🂵', '🂶', '🂷', '🂸', '🂹', '🂺', '🂻', '🂼', '🂽', '🂾', '🂡', '🂢', '��', '🂤', '🂥', '🂦', '🂧', '🂨', '🂩', '🂪', '🂫', '🂬', '🂭', '🂮', '🃁', '🃂', '🃃', '🃄', '🃅', '🃆', '🃇', '🃈', '🃉', '🃊', '🃋', '🃌', '🃍','🃑', '🃒', '🃓', '🃔', '🃕', '🃖', '🃗', '🃘', '🃙', '🃚', '🃛', '🃜', '🃝', '🃞']

    def __init__(self) -> None:
        self.players = []
        self.active_players = []
        self.deck = deck
        self.blinds = [10, 20]
        self.sb_i = 0
        self.running = False
        self.community = []
        self.correct_total_chips = 0

    def add_player(self, newPlayer):
        self.players.append(newPlayer)
        self.active_players.append(newPlayer)

        if isinstance(newPlayer, Human):
            self.human_player = newPlayer

        self.correct_total_chips += newPlayer.chips

    def start_move(self):
        if (
            self.current_player.all_in == True
            or self.current_player.fold == True
            or self.r >= self.skip_round
        ):

            self.current_player.agg = False  # Bad?
            end = self.end_move()  # skip move

            return False, end

        return True, None  # bad?

    def next_player(self, c=None):
        if c == None:
            c = self.cPI
        return (c + 1) % self.no_players

    def single_move(self, action=None):
        print("player remaining", self.players_remaining)

        valid = self.current_player.move(self, action)

        if not valid:
            print("not valid", action)
            return False

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
        if self.players_remaining == 1:
            self.end_hand()
            return False

        if self.current_player.agg:
            self.last_agg = self.cPI
            self.bets.append(self.current_player.round_invested)

        self.current_player.agg = False
        self.cPI = self.next_player()
        self.current_player = self.active_players[self.cPI]

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

        if self.r == 0:
            self.cPI = self.last_agg = (
                self.sb_i + (2 if self.no_players != 2 else 1)
            ) % self.no_players
            self.bets = [max(x.round_invested for x in self.active_players)]
            self.community = []
        else:
            self.cPI = self.last_agg = self.sb_i  # BUG here
            self.bets = [0]
            self.community = self.deck[
                self.communityCard_i : self.communityCard_i + self.r + 2
            ]

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

    def get_total_pot(self):
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
        old = self.active_players
        self.active_players = []
        button_bust = False

        for p in old:
            if p.chips:
                self.active_players.append(p)
            else:
                p.inactive = True
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

        self.active_in_hand = self.players_remaining = sum(
            [1 for p in self.active_players if not p.fold and not p.all_in]
        )
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
            sum(p.chips for p in self.players),
            len([1 for x in self.players if x.chips]),
        )
        if sum(p.chips for p in self.players) != self.correct_total_chips:
            raise Exception([p.chips for p in self.players])


def start():
    table1 = Table()
    profile_pictures = ["calvin", "elliot", "teddy", "bot", "daniel_n"]
    random.shuffle(profile_pictures)
    for r, p in enumerate(profile_pictures):
        if r == 0:
            chips = 2000
        else:
            chips = 2000
        table1.add_player(BotV1(r, p, table1, str(r), chips=chips))

    table1.add_player(
        Human(
            5,
            "nature",
            table1,
            str(5),
            chips=3000,
        )
    )
    return table1


def main():
    table1 = start()
    running = True
    while running:
        table1.start_hand()

        input("Click Enter for next hand: \n")


if __name__ == "__main__":
    main()

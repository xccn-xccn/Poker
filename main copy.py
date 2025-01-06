import random, time
from collections import deque
from copy import deepcopy
from deck import deck
from winner import get_winner


# BUG money appears out of nowwhere?
# TODO test valid bets on raises
# TODO account for sb or bb all in with blinds
# TODO Main pot and side pots
# TODO skip and show hands if only one player left
# TODO stop showing next round when everyone folds
# TODO auto call when all in
# TODO button should be sb heads up (not bb) fix this
# BUG negative pot 

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

        # self.position_i = (self.position_i - 1) % self.table.active_players

        a_player_count = len(self.table.active_players)
        self.position_i = ((i - self.table.sb_i) % a_player_count + 1) % a_player_count
        self.position_name = Player.pos_i_names[self.position_i]
        self.holeCards = self.table.deck[self.position_i * 2 : self.position_i * 2 + 2]

        if a_player_count == 2:
            self.total_invested = min(self.table.blinds[self.position_i], self.chips)
        elif self.position_i in [1, 2]:  # One of the blinds maybe change to name
            self.total_invested = min(self.table.blinds[self.position_i - 1], self.chips)
        else:
            self.total_invested = 0
        self.round_invested = self.total_invested

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
            self.extra = (
                roundTotal - self.round_invested
            )  # TODO Make side and main pots

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

            print(f"\n Your cards are {self.holeCards}{end}")

        prev_raise = table.blinds[-1]
        if len(table.bets) >= 2:
            prev_raise = table.bets[-1] - table.bets[-2]

        if action == 3: #BUG wrong
            if (
                (self.round_invested + extra < round_total + prev_raise and extra < self.chips)
                or extra > self.chips
            ):
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
    def get_bet(self, bets, table):

        prev_raise = table.blinds[-1]
        if len(bets) >= 2:
            prev_raise = bets[-1] - bets[-2]

        try:
            extra = random.randint(  # Check if this one works
                min(self.chips, bets[-1] - self.round_invested + prev_raise),
                min(max(bets[-1] * 2, int(table.get_total_pot() * 2.5)), self.chips),
            )

            if extra < 0:
                raise Exception

        except:
            print('ERROR', self.chips, bets, self.round_invested, prev_raise, table.pot)
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
        # self.active_players = 0

    def add_player(self, newPlayer):
        self.players.append(newPlayer)
        self.active_players.append(newPlayer)

        if isinstance(newPlayer, Human):
            self.human_player = newPlayer

    def start_move(self):
        if self.current_player.all_in == True or self.current_player.fold == True:

            self.current_player.agg = False  # Bad?
            end = self.end_move()  # skip move

            return False, end

        return True, None  # bad?

    def single_move(self, action=None):

        valid = self.current_player.move(self, action)

        if not valid:
            print("not valid")
            return False

        if self.current_player.fold == True:
            self.players_remaining -= 1

        print('pre', self.pot)
        self.set_pot()
        print('pot', self.pot)
        return self.end_move()

    def end_move(self):
        if self.players_remaining == 1:
            self.end_hand()

        if self.current_player.agg:
            self.last_agg = self.cPI
            self.bets.append(self.current_player.round_invested)

        self.cPI = (self.cPI + 1) % self.no_players
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
            self.cPI = self.last_agg = (self.sb_i + (2 if self.no_players != 2 else 1)) % self.no_players 
            self.bets = [*self.blinds]
            self.community = []
        else:
            self.cPI = self.last_agg = self.sb_i
            self.bets = [0]
            self.community = self.deck[
                self.communityCard_i : self.communityCard_i + self.r + 2
            ]

            print(f"{name[self.r]} Cards {self.community} pot {self.pot}")

        self.current_player = self.active_players[self.cPI]
        print(self.r, self.current_player.position_i, self.cPI)

    def set_pot(self, player=None):
        if player == None:
            player = self.current_player

        if player.fold == False:
            remaining = player.total_invested
            extra = player.extra
            p_name = player
            copy_pot = self.pot
            new_pot = []
            c_call = c_pot = saved = 0
            # print('copy', copy_pot, self.pot)
            print(p_name, remaining, extra)
            for index, p in enumerate(copy_pot):
                print('extra', extra)
                to_call = p[0]

                # print('start', p, to_call, remaining)
                if not remaining:
                    new_pot.append(p)
                elif to_call > remaining:
                    new = [remaining, remaining * (len(p[3]) + 1), player.all_in, p[3] | {p_name}]
                    p[0] -= remaining
                    p[1] -= len(p[3]) * remaining #think about this

                    if index == len(self.pot) -1:
                        p[1] -= remaining - extra #have to take away any collected pot that needs to be in this one
                    else:
                        self.pot[-1][1] -= remaining - extra
                    new_pot.append(new)
                    new_pot.append(p)
                    remaining = 0
                    
                else:
                    print('in1', remaining, to_call)
                    remaining -= to_call
                    if p[2] or remaining == 0: #do need to worry about smaller False pot before?
                        # print('in', remaining, p)
                        print('in2')
                        if p_name in p[3]:
                            new_pot.append(p)
                            continue
                        print('in3')
                        # p[0] += c_call
                        if remaining == 0:
                            p[1] += extra
                            print(extra - to_call, 'extra - to_call')
                        else:
                            p[1] += to_call

                        extra -= to_call
                        if extra < 0 and index != len(self.pot) - 1:
                            print('extra < 0', extra)
                            p[1] -= extra #subtracting negative
                            self.pot[-1][1] += extra
                            
                        # p[1] += to_call
                        p[3].add(p_name)
                        new_pot.append(p)
                        # c_call = c_pot = 0
                            
                    else: #BUG smaller bet
                        
                        c_call += to_call
                        c_pot += p[1]
                        if p_name not in p[3]: 
                            print('not in')
                            saved += to_call
                            extra -= to_call #extra less than 0 if player is taken out of pot

            if remaining:
                print('remaining', extra, to_call)
                new_pot.append([extra + c_call, extra + c_pot + saved, player.all_in, {p_name}])

            self.pot = new_pot
        else:
            for i in range(len(self.pot)):
                self.pot[i][3] = {x for x in self.pot[i][3] if x != player}


    def get_total_pot(self):
        return sum(p[1] for p in self.pot)

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
            self.sb_i = (self.sb_i + 1) % self.no_players
        self.pot = [[  0, 0, False, set()  ]] #to_call, pot_value, 1 or more players all in, players in pot
        self.r = 0

        random.shuffle(self.deck)

        for i, p in enumerate(self.active_players): #TODO account for if small blind is all in
            p.new_hand(i)
            # if p.round_invested:
            #     self.set_pot(p)
            if p.total_invested > self.pot[0][0]:
                self.pot[0][0] = p.total_invested
                self.pot[0][3] = {p}
                # self.pot[0][3] = {p.position_name}

            self.pot[0][1] += p.total_invested
            self.pot[0][2] = self.pot[0][2] or p.all_in

        print('pot', self.pot)
        self.players_remaining = sum(
            [1 for p in self.active_players if not p.fold]
        )  # have to do this because possible that one of the blinds is put all in by the blinds
        self.communityCard_i = self.no_players * 2

        self.end_round(start=True)

    def give_pot(self, pot):
        c_players = pot[3]

        if self.players_remaining > 1:
            wInfo = get_winner([p.holeCards for p in c_players], self.community)
        else:
            wInfo = [[None, 0]]

        wHand = wInfo[0][0]
        wPIs = [x[1] for x in wInfo]
        winners = [p for i, p in enumerate(c_players) if i in wPIs]

        for w_p in winners:
            print(w_p.chips, pot)
            w_p.chips += pot[1] // len(winners)
            print(w_p.chips)

        if wHand:
            end = f"with {wHand}"
        else:
            end = ""

        print([x.position_name for x in c_players])

        print(
            f"{'Winner' if len(winners) == 1 else 'Winners'} {', '.join([p.position_name for p in winners])} wins {pot} chips {end}"
        )

        print("Testing", [x.holeCards for x in c_players], self.community)

    def end_hand(self):
        self.running = False

        for i in range(len(self.pot) - 1, -1, -1):
            self.give_pot(self.pot[i])

def start():
    table1 = Table()
    profile_pictures = ["calvin", "elliot", "teddy", "bot", "daniel_n"]
    random.shuffle(profile_pictures)
    for r, p in enumerate(profile_pictures):
        if r == 0:
            chips = 2000
        else:
            chips = 1
        table1.add_player(Bot(r, p, table1, str(r), chips=chips))

    table1.add_player(
        Human(
            5,
            "nature",
            table1,
            str(5),
            chips=2000,
            
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
    # main()
    p1 = Bot(0, 0, 0)
    p2 = Bot(0, 0, 0)
    # a = set()
    # a.add(p1)
    # a.add(p2)
    for x in (p1, p2):
        x.chips = 0
    print(p1.chips)
    p1.chips = 100
    # a.add(p1)
    # print(a)
    pass

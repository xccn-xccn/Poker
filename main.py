import random, time
from deck import deck
from winner import get_winner


# BUG money appears out of nowwhere?
# BUG BB sometimes folds when he can just check?
# TODO Skip positions when players have ran out of money !!
# Main pot and side pots
# BUG if multiple players run out of money in the same round several player can reset to index 0


class Player:
    pos_names = {
        1: "Button",
        2: "Small blind",
        3: "Big blind",
        4: "UTG",
        5: "Hijack",
        6: "Cutoff",
        
    }

    def __init__(self, position, profile_picture, chips=1000):
        self.chips = chips
        self.position = self.table_position = position
        self.profile_picture = profile_picture
        self.inactive = False

    def set_pos_names(self, players):
        self.pos_names = {}
        for i, pos in enumerate([*["UTG" + (f" +{n}" if n != 0 else "") for n in range(max(players-5, 0))], "Lojack", "Hijack", "Cutoff", "Button", "Small blind", "Big blind"][-players:]):
            self.pos_names[i + 1] = pos

        


    def new_hand(self, deck, blinds, no_players):

        self.fold = False
        self.agg = False
        if self.chips <= 0:
            self.fold = True

        self.position = self.position - 1
        self.position = (
            no_players if self.position == 0 else self.position
        ) 

        i = self.position - 1
        self.positionName = Player.pos_names[self.position]
        self.holeCards = deck[i * 2 : i * 2 + 2]

        if self.position in [2, 3]:  # One of the blinds
            self.totalInvested = min(blinds[i-1], self.chips)
        else:
            self.totalInvested = 0
        self.round_invested = self.totalInvested

        self.chips -= self.round_invested
        self.allIn = not (bool(self.chips) or self.fold)

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
                self.allIn = True
                self.extra = self.chips

        else:
            self.action_text = f"bets {self.extra}"

            self.agg = True

        self.round_invested += self.extra
        self.chips -= self.extra

        if self.chips == 0:
            self.allIn = True

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

        if action == 3:
            if (
                self.round_invested + extra < min(round_total + prev_raise, self.chips)
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
            f"\n {self.positionName} {name} {self.action_text} with {self.chips} chips behind {self.round_invested} invested this round"
        )

        return True


class Bot(Player):
    def get_bet(self, bets, table):

        prev_raise = table.blinds[-1]
        if len(bets) >= 2:
            prev_raise = bets[-1] - bets[-2]

        try:
            extra = random.randint(  # Check if this one works
                min(self.chips, bets[-1] - self.round_invested + prev_raise),
                min(max(bets[-1] * 2, int(table.pot * 2.5)), self.chips),
            )

            if extra < 0:
                raise Exception

        except:
            print(self.chips, bets, self.round_invested, prev_raise, table.pot)
            print(
                min(self.chips, bets[-1] - self.round_invested + prev_raise),
                min(int(table.pot * 2.5), self.chips),
            )
            raise Exception

        return extra

    def get_action(self, table):
        bets = table.bets
        round_total = bets[-1]
        l = 1
        h = 3
        if round_total == 0:
            l = 2
        if table.bets[-1] >= self.round_invested + self.chips:
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
        self.sb_i = 1
        self.running = False
        self.community = []
        # self.active_players = 0

    def add_player(self, newPlayer):
        self.players.append(newPlayer)
        self.active_players.append(newPlayer)

        if isinstance(newPlayer, Human):
            self.human_player = newPlayer


    def start_move(self):
        if self.currentPlayer.allIn == True or self.currentPlayer.fold == True:

            self.currentPlayer.agg = False  # Bad?
            end = self.end_move()  # skip move

            return False, end

        return True, None  # bad?

    def single_move(self, action=None):

        valid = self.currentPlayer.move(self, action)

        if not valid:
            print("not valid")
            return False

        self.pot += self.currentPlayer.extra

        if self.currentPlayer.fold == True:
            self.players_remaining -= 1

        return self.end_move()

    def end_move(self):
        if self.players_remaining == 1:
            self.end_hand()

        if self.currentPlayer.agg:
            self.last_agg = self.cPI
            self.bets.append(self.currentPlayer.round_invested)

        self.cPI = (self.cPI + 1) % self.no_players
        self.currentPlayer = self.active_players[self.cPI]

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
            self.cPI = self.last_agg = (self.sb_i + 2) % self.no_players
            self.bets = [self.blinds[1]]
            self.community = []
        else:
            self.cPI = self.last_agg = self.sb_i
            self.bets = [0]
            self.community = self.deck[
                self.communityCard_i : self.communityCard_i + self.r + 2
            ]

            print(f"{name[self.r]} Cards {self.community} pot {self.pot}")

        self.currentPlayer = self.active_players[self.cPI]
        print(self.r, self.currentPlayer.position, self.cPI)
    def start_hand(self):
        self.running = True
        old = self.active_players
        self.active_players = []

        for p in old:
            if p.chips:
                self.active_players.append(p)
            else:
                p.inactive = True


        self.no_players = len(self.active_players)

        self.sb_i = (self.sb_i + 1) % self.no_players
        self.pot = 0
        self.r = 0

        random.shuffle(self.deck)

        for p in self.active_players:
            p.new_hand(self.deck, self.blinds, self.no_players)
            self.pot += p.round_invested

        self.players_remaining = sum([1 for p in self.active_players if not p.fold])  #have to do this because possible that one of the blinds is put all in by the blinds
        self.communityCard_i = self.no_players * 2

        self.end_round(start=True)

    def end_hand(self):
        self.running = False

        c_players = [p for p in self.active_players if not p.fold]

        if self.players_remaining > 1:
            wInfo = get_winner([p.holeCards for p in c_players], self.community)
        else:
            wInfo = [[None, 1]]

        wHand = wInfo[0][0]
        wPIs = [x[1] - 1 for x in wInfo]
        winners = [p for i, p in enumerate(c_players) if i in wPIs]

        for wP in winners:
            wP.chips += self.pot // len(winners)

        if wHand:
            end = f"with {wHand}"
        else:
            end = ""

        print([x.positionName for x in c_players])

        print(
            f"{'Winner' if len(winners) == 1 else 'Winners'} {', '.join([p.positionName for p in winners])} wins {self.pot} chips {end}"
        )

        print("Testing", [x.holeCards for x in c_players], self.community)


def start():
    table1 = Table()
    profile_pictures = ["calvin", "elliot", "teddy", "bot", "daniel_n"]
    random.shuffle(profile_pictures)
    for r, p in zip(range(5), profile_pictures):
        if r == 0:
            chips = 20
        else:
            chips = 1000
        table1.add_player(Bot(r + 1, p, chips=chips))

    table1.add_player(
        Human(
            6,
            "nature",
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
    main()

    pass

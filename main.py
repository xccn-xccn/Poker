import random, time
from deck import deck
from winner import get_winner

# sb_i refers to the player who is the small blind in the list self.players self.postion refers to the position of the player 1 is sb


# BUG blinds can put players into the negative
# TODO Make GUI
# TODO use os.path to use relative path instead of absolute path
# TODO Min bet, Skip positions when players have ran out of money
# Main pot and side pots
class Player:
    pos_names = {
        1: "Small blind",
        2: "Big blind",
        3: "UTG",
        4: "Hijack",
        5: "Cutoff",
        6: "Button",
    }

    def __init__(self, position, chips=1000) -> None:
        self.chips = chips
        self.position = position

    def new_hand(self, deck, blinds):

        self.fold = False
        self.allIn = False
        if self.chips <= 0:
            print("Player is Broke")
            self.fold = True

        self.position = self.position - 1  # TODO important change this to be dynamic
        self.position = (
            6 if self.position == 0 else self.position
        )  # TODO important change this to be dynamic
        #line 39 BUG
        i = self.position - 1
        self.positionName = Player.pos_names[self.position]
        self.holeCards = deck[i * 2 : i * 2 + 2]

        if self.position <= 2:  # One of the blinds
            self.totalInvested = blinds[i]
        else:
            self.totalInvested = 0
        self.roundInvested = self.totalInvested

        self.chips -= self.roundInvested

    def end_round(self):
        self.roundInvested = 0

    def move_action(self, roundTotal):
        print("action", self.action)
        if self.action == 1:  # change maybe
            self.actionText = "folds"
            self.fold = True
            self.agg = False
            self.extra = 0

        elif self.action == 2:

            self.agg = False
            self.extra = roundTotal - self.roundInvested  # TODO Make side and main pots

            self.actionText = "calls" if self.extra else "checks"

            if roundTotal >= self.roundInvested + self.chips:
                self.allIn = True
                self.extra = self.chips

        else:
            self.actionText = f"bets {self.extra}"

            self.agg = True

        self.roundInvested += self.extra
        self.chips -= self.extra


    def is_valid(self, roundTotal, pot, community, action):
        if len(action) == 2:
            self.action, self.extra = action
        else:
            self.action, self.extra = action, 0

        if action == 3 and roundTotal >= self.roundInvested + self.chips:
            return False

        if action == 3:
            if self.roundInvested + self.extra < roundTotal or self.extra > self.chips:
                return False


        return True
    
class Bot(Player):
    def get_bet(self, roundTotal):
        extra = random.randint(
            roundTotal - self.roundInvested, self.chips
        )  # BUG Int rounding not trustworthy TODO make max bet half chips

        return extra

    def get_action(self, roundTotal):
        l = 1
        h = 3 
        if roundTotal == 0:
            l = 2
        if roundTotal >= self.roundInvested + self.chips:
            h = 2 
            l = 2

        action = random.randint(l, h)

        if action == 3:
            bet = self.get_bet(roundTotal)
        else:
            bet = 0
        return action, bet

    def move(self, roundTotal, pot, community, action):

        valid = self.is_valid(roundTotal, pot, community, action)
        
        if not valid:
            raise Exception
            return False
        
        super().move_action(roundTotal)

        print(
            f"{self.positionName} {self.actionText} with {self.chips} chips behind {self.roundInvested} invested this round"
        )

        return True

class Human(Player):

    def get_bet(self, roundTotal):

        self.extra = -1

        while self.extra < 0:
            # print("Invalid Bet")
            time.sleep(1)

        while True:

            if self.roundInvested + self.extra < roundTotal:
                # print("Bet is too small ")
                time.sleep(1)
                continue

            if self.extra > self.chips:
                # print(("Bet is too large "))
                time.sleep(1)
                continue

            return self.extra  # bad practice?

    def is_valid(self, roundTotal, pot, community, action):
        if len(action) == 2:
            self.action, self.extra = action
        else:
            self.action, self.extra = action, 0


        if community:
            end = f", Community Cards {community}"
        else:
            end = ""

        print(f"Your cards are {self.holeCards}{end}")

        if action == 3 and roundTotal >= self.roundInvested + self.chips:
            return False

        if action == 3:
            if self.roundInvested + self.extra < roundTotal or self.extra > self.chips:
                return False


        return True

    def move(self, roundTotal, pot, community, action):
        valid = self.is_valid(roundTotal, pot, community, action)

        if not valid:
            return False
        
        super().move_action(roundTotal)

        print(
            f"{self.positionName} (YOU) {self.actionText} with {self.chips} chips behind {self.roundInvested} invested this round"
        )
        # Only printing for testing

        return True


class Table:
    # deck = ['🂱', '🂲', '🂳', '🂴', '🂵', '🂶', '🂷', '🂸', '🂹', '🂺', '🂻', '🂼', '🂽', '🂾', '🂡', '🂢', '��', '🂤', '🂥', '🂦', '🂧', '🂨', '🂩', '🂪', '🂫', '🂬', '🂭', '🂮', '🃁', '🃂', '🃃', '🃄', '🃅', '🃆', '🃇', '🃈', '🃉', '🃊', '🃋', '🃌', '🃍','🃑', '🃒', '🃓', '🃔', '🃕', '🃖', '🃗', '🃘', '🃙', '🃚', '🃛', '🃜', '🃝', '🃞']

    def __init__(self) -> None:
        self.players = []
        self.deck = deck
        self.blinds = [20, 40]
        self.sb_i = 6
        self.running = False
        self.community = []

    def add_player(self, newPlayer):
        self.players.append(newPlayer)

        if isinstance(newPlayer, Human):
            self.human_player = newPlayer.position

    def start_move(self):
        self.agg = False
        if self.currentPlayer.allIn == True or self.currentPlayer.fold == True:
            print(
                f"{self.currentPlayer.positionName} is all in / folded so turn is skipped {self.currentPlayer.chips} behind (should be 0)"
            )
            self.end_move()  # skip move
            return False
        return True

    def single_move(self, action=None):

        valid = self.currentPlayer.move(
            self.roundTotal, self.pot, self.community, action
        )

        if not valid:
            return False
        
        self.pot += self.currentPlayer.extra

        if self.currentPlayer.fold == True:
            self.playerRemaining -= 1

        self.end_move()

    def end_move(self):
        if self.playerRemaining == 1:
            self.end_hand()

        if self.currentPlayer.agg:
            self.last_agg = self.cPI
            self.roundTotal = self.currentPlayer.roundInvested

        self.cPI = (self.cPI + 1) % self.noPlayers
        self.currentPlayer = self.players[self.cPI]

        print(self.cPI)

        if self.last_agg == self.cPI:
            self.end_round()

    def end_round(self, start=False):
        if not start:
            self.r += 1

            for p in self.players:
                p.roundInvested = 0

        for p in self.players:
            p.action = p.actionText = None 
            
        if self.r == 4:
            self.end_hand()
            return 

        name = {0: "Pre Flop", 1: "Flop", 2: "Turn", 3: "River"}

        if self.r == 0:
            print("Pre Flop")
            self.cPI = self.last_agg = (self.sb_i + 2) % self.noPlayers
            self.roundTotal = self.blinds[1]
            self.community = []
        else:
            self.cPI = self.last_agg = self.sb_i
            self.roundTotal = 0
            self.community = self.deck[
                self.communityCard_i : self.communityCard_i + self.r + 2
            ]

            print(f"{name[self.r]} Cards {self.community}")

        self.currentPlayer = self.players[self.cPI]

    def start_hand(self):
        self.running = True
        self.sb_i = (self.sb_i + 1) % 6
        self.noPlayers = len(self.players)
        self.pot = sum(self.blinds)
        self.r = 0

        random.shuffle(self.deck)

        for p in self.players:
            p.new_hand(self.deck, self.blinds)

        self.playerRemaining = sum([1 for p in self.players if not p.fold])  # Check
        self.communityCard_i = (
            self.noPlayers * 2
        )  # the index of the first card to be drawn in the flop

        self.end_round(start=True)
    def end_hand(self):
        self.running = False

        c_players = [p for p in self.players if not p.fold]

        print([x.positionName for x in c_players])

        if self.playerRemaining > 1:
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

        print(
            f"{'Winner' if len(winners) == 1 else 'Winners'} {', '.join([p.positionName for p in winners])} wins {self.pot} chips {end}"
        )

        print("Testing", [x.holeCards for x in c_players], self.community)


def start():
    table1 = Table()

    for r in range(5):
        table1.add_player(Bot(r + 1))

    table1.add_player(Human(6, chips=2000))
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

import random
from deck import deck
from winner import get_winner

# sb_i refers to the player who is the small blind in the list self.players self.postion refers to the position of the player 1 is sb


# BUG blinds can put players into the negative
# TODO Make GUI, Draws
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

        self.position = self.position + 1  # TODO important change this to be dynamic
        self.position = (
            1 if self.position == 7 else self.position
        )  # TODO important change this to be dynamic

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

    def move_action(self, action, roundTotal):
        if action == 1:  # change maybe
            actionText = "folds"
            self.fold = True
            agg = False
            extra = 0

        elif action == 2:

            agg = False
            extra = roundTotal - self.roundInvested  # TODO Make side and main pots

            actionText = "calls" if extra else "checks"

            if roundTotal >= self.roundInvested + self.chips:
                self.allIn = True
                extra = self.chips

        else:
            extra = self.get_bet(roundTotal)

            actionText = f"bets {extra}"

            agg = True

        self.roundInvested += extra
        self.chips -= extra

        return agg, self.roundInvested, extra, actionText

    def move(self):
        pass


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

        return action

    def move(self, roundTotal, pot, community):

        action = self.get_action(roundTotal)

        agg, self.roundInvested, extra, actionText = super().move_action(
            action, roundTotal
        )

        print(
            f"{self.positionName} {actionText} with {self.chips} chips behind {self.roundInvested} invested this round"
        )
        return agg, self.roundInvested, extra


class Human(Player):

    def get_bet(self, roundTotal):

        extra = int(input("How much is your bet "))

        while True:

            if self.roundInvested + extra < roundTotal:
                extra = int(input("Bet is too small "))
                continue

            if extra > self.chips:
                extra = int(input("Bet is too large "))
                continue

            return extra  # bad practice?

    def display_message(self, roundTotal, pot, community):

        valid = [1, 2, 3]
        option3 = "3 Bet"

        if community:
            end = f", Community Cards {community}"
        else:
            end = ""

        print(f"Your cards are {self.holeCards}{end}")

        if roundTotal == self.roundInvested:  # should not be possible to be less
            option2 = "2 Check"
        elif roundTotal >= self.roundInvested + self.chips:
            option2 = f"2 Call (All In) {roundTotal - self.roundInvested}"
            option3 = ""
            valid = [1, 2]
        else:
            option2 = f"2 Call {roundTotal - self.roundInvested}"

        message = f"""[Name] Enter your move you are {self.positionName}, you have {self.chips} chips, you have invested {self.roundInvested} in this round so far - pot {pot}:
            1 Fold
            {option2}
            {option3}
            Current table bet {roundTotal} \n"""

        return message, valid

    def get_action(self, roundTotal, pot, community):

        message, valid = self.display_message(roundTotal, pot, community)

        action = int(input(message))

        while action not in valid:
            action = int(input("Re-enter move "))
        return action

    def move(self, roundTotal, pot, community):

        action = self.get_action(roundTotal, pot, community)

        agg, self.roundInvested, extra, actionText = super().move_action(
            action, roundTotal
        )

        print(
            f"{self.positionName} (YOU) {actionText} with {self.chips} chips behind {self.roundInvested} invested this round"
        )
        # Only printing for testing
        return agg, self.roundInvested, extra


class Table:
    # deck = ['🂱', '🂲', '🂳', '🂴', '🂵', '🂶', '🂷', '🂸', '🂹', '🂺', '🂻', '🂼', '🂽', '🂾', '🂡', '🂢', '��', '🂤', '🂥', '🂦', '🂧', '🂨', '🂩', '🂪', '🂫', '🂬', '🂭', '🂮', '🃁', '🃂', '🃃', '🃄', '🃅', '🃆', '🃇', '🃈', '🃉', '🃊', '🃋', '🃌', '🃍','🃑', '🃒', '🃓', '🃔', '🃕', '🃖', '🃗', '🃘', '🃙', '🃚', '🃛', '🃜', '🃝', '🃞']

    def __init__(self) -> None:
        self.players = []
        self.deck = deck
        self.blinds = [20, 40]

    def add_player(self, newPlayer):
        self.players.append(newPlayer)

    def hand(self, sb_i):
        self.noPlayers = len(self.players)
        self.pot = sum(self.blinds)

        random.shuffle(self.deck)

        for p in self.players:
            p.new_hand(self.deck, self.blinds)

        self.playerRemaining = sum([1 for p in self.players if not p.fold])  # Check
        self.communityCard_i = (
            self.noPlayers * 2
        )  # the index of the first card to be drawn in the flop
        for r in range(0, 4):
            self.s_round(r, sb_i)

            if self.playerRemaining == 1:
                break
            for p in self.players:
                p.end_round()

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

    def s_round(self, r, sb_i):
        name = {0: "Pre Flop", 1: "Flop", 2: "Turn", 3: "River"}

        if r == 0:
            print("Pre Flop")
            cPI = (sb_i + 2) % self.noPlayers
            self.community = None
        else:
            cPI = sb_i
            n = r + 2

            self.community = self.deck[self.communityCard_i : self.communityCard_i + n]

            print(f"{name[r]} Cards {self.community}")

        self.roundTotal = 0 if r != 0 else self.blinds[1]

        cont = True
        if r == 0:
            last_agg = (sb_i + 2) % self.noPlayers  # last aggressor index
        else:
            last_agg = (sb_i) % self.noPlayers

        while cont:
            agg = False
            if self.playerRemaining == 1:
                return
            currentPlayer = self.players[cPI]

            if currentPlayer.allIn == True:
                print(
                    f"{currentPlayer.positionName} is all in so turn is skipped {currentPlayer.chips} behind (should be 0)"
                )
            elif currentPlayer.fold == False:

                agg, invested, bet = currentPlayer.move(
                    self.roundTotal, self.pot, self.community
                )
                self.pot += bet

                if currentPlayer.fold == True:
                    self.playerRemaining -= 1

            if agg:
                last_agg = cPI
                self.roundTotal = invested
            else:
                if last_agg == (cPI + 1) % self.noPlayers:
                    break
            cPI = (cPI + 1) % self.noPlayers


def start():
    table1 = Table()

    for r in range(5):
        table1.add_player(Bot(r + 1))

    table1.add_player(Human(6, chips=2000))
    return table1


def main():
    table1 = start()
    running = True
    sb_i = 5
    while running:
        table1.hand(sb_i)
        sb_i = (sb_i - 1) % 6

        input("Click Enter for next hand: \n")


if __name__ == "__main__":
    main()

    pass

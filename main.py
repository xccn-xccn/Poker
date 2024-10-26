import random
from deck import deck
from winner import get_winner

# sb_i refers to the player who is the small blind in the list self.players self.postion refers to the position of the player 1 is sb

# BUG Players can decide to bet when they have to go all in but the betting size is either too little to call but more than players chips
# TODO Make small functions for Player.move to reduce repetition between Bot and Human, make all in attribute
# TODO Make GUI
# TODO Min bet, Skip positions when players have ran out of money Implement all in
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

    def __init__(self, position) -> None:
        self.chips = 1000
        self.position = position

    def new_hand(self, deck, blinds):

        self.fold = False

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
            self.invested = blinds[i]
        else:
            self.invested = 0

        self.chips -= self.invested

    def set_bet(self, val=0):
        self.invested = val

    def move(self):
        pass


class Bot(Player):
    def move(self, roundTotal, pot, community):

        if self.fold:
            return

        l = 1
        h = 3
        if roundTotal == 0: 
            l = 2
        if roundTotal >= self.invested + self.chips: #all in BUG round ends but self.invested does not change?
            h = 2
            l = 2
        
        action = random.randint(l, h)
        if action == 1:  # change maybe
            actionText = "folds"
            self.fold = True
            agg = False
            extra = 0

        elif action == 2:

            agg = False
            extra = roundTotal - self.invested #TODO Make side and main pots

            actionText = "calls" if extra else "checks"
            # self.invested = roundTotal #TODO Make side and main pots

            if roundTotal >= self.invested + self.chips: #all in
                extra = self.chips

        else:
            extra = random.randint(roundTotal-self.invested, self.chips) # BUG Int rounding not trustworthy TODO make max bet half chips


            if self.invested + extra < roundTotal:
                raise Exception

            if extra > self.chips:
                raise Exception



            
            actionText = f"bets {extra}"

            
            agg = True

        self.invested += extra
        self.chips -= extra

        print(f"{self.positionName} {actionText} with {self.chips} chips behind")
        return agg, self.invested, extra


class Human(Player):

    def __init__(self, position):
        super().__init__(position)

    def move(self, roundTotal, pot, community):
        # super().move()  # check if return in the parent function actually ends it (it doesnt)

        if self.fold:
            return

        if community:
            end = f", Community Cards {community}"
        else:
            end = ""

        print(f"Your cards are {self.holeCards}{end}")

        if roundTotal == self.invested:  # should not be possible to be less
            option2 = "2 Check"
        else:
            option2 = f"2 Call {roundTotal - self.invested}"
        message = f"""[Name] Enter your move you are {self.positionName}, you have {self.chips} chips, you have invested {self.invested} in this round so far - pot {pot}:
            1 Fold
            {option2}
            3 Bet
            Current table bet {roundTotal} \n"""

        action = int(input(message))

        while action not in [1, 2, 3]:
            action = int(input("Re-enter move "))

        if action == 1:  # change maybe
            self.fold = True
            agg = False
            extra = 0

        elif action == 2:
            agg = False
            extra = roundTotal - self.invested
            self.invested = roundTotal

            if roundTotal > self.invested + self.chips: #all in negative chips if too much money all in - only somtimes??
                extra = self.chips
        else:
            extra = int(input("How much is your bet "))

            while True:

                if self.invested + extra < roundTotal:
                    extra = int(input("Bet is too small "))
                    continue

                if extra > self.chips:
                    extra = int(input("Bet is too large "))
                    continue

                break

            
            agg = True

        self.invested += extra
        self.chips -= extra

        return agg, self.invested, extra


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

        
        self.playerRemaining = sum([1 for p in self.players if not p.fold]) #Check
        self.communityCard_i = (
            self.noPlayers * 2
        )  # the index of the first card to be drawn in the flop
        for r in range(0, 4):
            self.s_round(r, sb_i)

            if self.playerRemaining == 1:
                break
            for p in self.players:
                p.set_bet()

        c_players = [p for p in self.players if not p.fold]
        if self.playerRemaining > 1:

            wInfo = get_winner([p.holeCards for p in c_players], self.community)
        else:
            wInfo = [[None, 1]]
        if len(wInfo) == 1:
            wHand, wPI = wInfo[0]
            wPI -= 1
            wPlayer = c_players[wPI]

            if wHand:
                end = f"with {wHand}"
            else:
                end = ""
            print(f"Winner {wPlayer.positionName} wins {self.pot} chips {end}")

            wPlayer.chips += self.pot

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

        self.to_call = 0 if r != 0 else self.blinds[1]

        cont = True
        if r == 0:
            last_agg = (sb_i + 2) % self.noPlayers  # last aggressor index
        else:
            last_agg = (
                sb_i
            ) % self.noPlayers  # last aggressor is set to the sb so that at the end of the buttons turn, the next player who would be the sb is checked and the round ends
        # agg = False
        while cont:
            if self.playerRemaining == 1:
                return
            currentPlayer = self.players[cPI]

            # print("position", currentPlayer.position, cPI, last_agg, currentPlayer.fold)
            if currentPlayer.fold != True:

                agg, invested, bet = currentPlayer.move(
                    self.to_call, self.pot, self.community
                )
                self.pot += bet

                if currentPlayer.fold == True:
                    self.playerRemaining -= 1
            else:
                agg = False

            if agg:  # if the player just made an aggresive move (any bet / raise)
                last_agg = cPI
                self.to_call = invested
            else:  # if the player was also the last person to make an aggresive move
                if last_agg == (cPI + 1) % self.noPlayers:
                    break
            cPI = (cPI + 1) % self.noPlayers  # current player index


def start():
    table1 = Table()

    for r in range(5):
        table1.add_player(Bot(r + 1))

    table1.add_player(Human(6))
    return table1


def main():
    table1 = start()
    running = True
    sb_i = 5
    while running:
        table1.hand(sb_i)
        sb_i = (sb_i - 1) % 6


if __name__ == "__main__":
    main()

    pass

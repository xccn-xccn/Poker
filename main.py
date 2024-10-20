import random
#sb_i refers to the player who is the small blind in the list self.players self.postion refers to the position of the player 1 is sb

#Make money 
class Player:
    pos_names = {1: "Small blind", 2: "Big blind", 3: "UTG", 4: "Hijack", 5: "Cutoff", 6: "Button"}
    def __init__(self, position) -> None:
        self.chips = 1000
        self.position = position

    def new_hand(self, deck, blinds):
        self.fold = False

        self.position = (self.position + 1) #TODO important change this to be dynamic
        self.position = 1 if self.position == 7 else self.position #TODO important change this to be dynamic

        i = self.position - 1
        self.positionName = Player.pos_names[self.position]
        self.holeCards = deck[i * 2 : i * 2 + 2]

        if self.position <= 2: #One of the blinds
            self.bet = blinds[i]
        else:
            self.bet = 0

    def set_bet(self, val = 0):
        self.bet = val

    def move(self):
        if self.fold:
            return

    
class Human(Player):

    def __init__(self, position):
        super().__init__(position)

    def move(self, to_call, pot):
        super().move() #check if return in the parent function actually ends it (it doesnt)
        
        if self.fold:
            return
        
        print(f"Your cards are {self.holeCards}")
        
        if to_call == self.bet: #should not be possible to be less
            option2 = "2 Check"
        else:
            option2 = f"2 Call {to_call - self.bet}"
        message = f"""[Name] Enter your move you are {self.positionName} you have invested {self.bet} in this round so far pot {pot}:
            1 Fold
            {option2}
            3 Bet
            Current table bet {to_call} \n"""

        action = int(input(message))
        
        while action not in [1, 2, 3]:
            action = int(input("Re-enter move "))

        if action == 1:
            self.fold = True
            return False, self.bet, 0 #TODO Change
        elif action == 2:
            extra = to_call - self.bet
            self.bet = to_call
            return False, self.bet, extra
        else:
            extra = int(input("How much is your bet "))

            while self.bet + extra < to_call:
                extra = int(input("Bet is too small "))

            self.bet += extra
            return True, self.bet, extra
        



class Table:
    # deck = ['🂱', '🂲', '🂳', '🂴', '🂵', '🂶', '🂷', '🂸', '🂹', '🂺', '🂻', '🂼', '🂽', '🂾', '🂡', '🂢', '��', '🂤', '🂥', '🂦', '🂧', '🂨', '🂩', '🂪', '🂫', '🂬', '🂭', '🂮', '🃁', '🃂', '🃃', '🃄', '🃅', '🃆', '🃇', '🃈', '🃉', '🃊', '🃋', '🃌', '🃍','🃑', '🃒', '🃓', '🃔', '🃕', '🃖', '🃗', '🃘', '🃙', '🃚', '🃛', '🃜', '🃝', '🃞']
    
    def __init__(self) -> None:
        self.players = []
        self.deck = ['AC', '2C', '3C', '4C', '5C', '6C', '7C', '8C', '9C', 'TC', 'JC', 'QC', 'KC', 'AS', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', 'TS', 'JS', 'QS', 'KS', 'AH', '2H', '3H', '4H', '5H', '6H', '7H', '8H', '9H', 'TH', 'JH', 'QH', 'KH', 'AD', '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', 'TD', 'JD', 'QD', 'KD']
        self.blinds = [20, 40]

    def add_player(self, newPlayer):
        self.players.append(newPlayer)

    def hand(self, sb_i):
        self.noPlayers = len(self.players)
        self.pot = sum(self.blinds)

        random.shuffle(self.deck)

        for p in self.players:
            p.new_hand(self.deck, self.blinds)

        self.communityCard_i = self.noPlayers * 2 #the index of the next card to be drawn
        for r in range(0, 4):
            self.s_round(r, sb_i) 

            for p in self.players:
                p.set_bet()

        
    def s_round(self, r, sb_i):
        name = {0: "Pre Flop", 1: "Flop", 2: "Turn", 3: "River"}

        if r == 0:
            print("Pre Flop")
            cPI = (sb_i + 2) % self.noPlayers
        else:
            cPI = sb_i 
            n = r + 2
            
            community = self.deck[self.communityCard_i: self.communityCard_i + n]

            print(f"{name[r]} Cards {community}")

        self.to_call = 0 if r != 0 else self.blinds[1]

        cont = True
        if r == 0:
            last_agg = (sb_i + 2) % self.noPlayers #last aggressor index
        else:
            last_agg = (sb_i) % self.noPlayers #last aggressor is set to the sb so that at the end of the buttons turn, the next player who would be the sb is checked and the round ends
        # agg = False
        while cont:
            
            currentPlayer = self.players[cPI] 

            print("position", currentPlayer.position, cPI, last_agg, currentPlayer.fold)
            if currentPlayer.fold != True:

                agg, invested, bet = currentPlayer.move(self.to_call, self.pot)
                self.pot += bet
            else:
                agg = False
            
            print(agg, last_agg)
            if agg: #if the player just made an aggresive move (any bet / raise) 
                last_agg = cPI
                self.to_call = invested
            else: #if the player was also the last person to make an aggresive move
                if last_agg == (cPI + 1) % self.noPlayers:
                    break
            print(agg, last_agg, "!!!!")
            cPI = (cPI+1) % self.noPlayers #current player index
            


def start():
    table1 = Table()

    for r in range(6):
        table1.add_player(Human(r + 1))
    return table1


def main():
    table1 = start()
    running = True
    sb_i = 5
    while running:
        table1.hand(sb_i)
        sb_i = (sb_i + 1) % 6


if __name__ == "__main__":
    main()

    pass
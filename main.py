import random
#sb_i refers to the player who is the small blind in the list self.players self.postion refers to the position of the player 1 is sb

#TODO make UTG act first if it is pre flop else sb also check why position starts on Cutoff (should be UTG) works
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
        self.holeCards = deck[i : i + 2]

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

    def move(self, to_call):
        super().move() #check if return in the parent function actually ends it
        
        if self.fold:
            return
        
        if to_call > self.bet:
            valid = [1, 2, 3]
            message = f"""[Name] Enter your move you are {self.positionName} you have bet {self.bet} in this round so far:
                1 Fold
                2 Check
                3 Bet
                Current table bet {to_call} \n"""
        else:
            valid = [1, 3]
            message = f"""[Name] Enter your move you are {self.positionName} you have bet {self.bet} in this round so far:
                1 Fold
                3 Bet
                Current table bet {to_call} \n"""

        action = int(input(message))
        
        while action not in valid:
            action = int(input("Re-enter move"))

        if action == 1:
            self.fold = True
        elif action == 2:
            self.bet = 0
        else:
            self.bet = int(input("How much is your bet"))
            return True, self.bet
        



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
        random.shuffle(self.deck)

        for i, p in enumerate(self.players):
            p.new_hand(self.deck, self.blinds)

        self.nextCard_i = self.noPlayers * 2 #the index of the next card to be drawn
        for r in range(0, 4):
            self.s_round(r, sb_i) 

            for p in self.players:
                p.set_bet()

        
    def s_round(self, r, sb_i):
        name = {0: "Pre Flop", 1: "Flop", 2: "Turn", 3: "River"}

        if r == 0:
            print("Pre Flop")
        else:
            n = 1
            if r == 1:
                n = 3

            revealed = self.deck[self.nextCard_i: self.nextCard_i + n]
            self.nextCard_i += n

            print(self.nextCard_i, self.nextCard_i + n)
            print(f"{name[r]} Cards revealed {revealed}")

        self.to_call = 0 if r else self.blinds[1]

        c = sb_i + 2
        cont = True
        last_agg = sb_i + 1
        while cont:
            info = self.players[c].move(self.to_call)
            if info:
                agg, self.to_call = info
            else:
                agg = False
            c = (c+1) % self.noPlayers

            if agg: #if the player just made an aggresive move (any bet / raise)
                last_agg = c
            else: #if the player was also the last person to make an aggresive move
                if last_agg == c:
                    break
            


def start():
    table1 = Table()

    for r in range(6):
        table1.add_player(Human(r + 1))
    return table1


def main():
    table1 = start()
    running = True
    sb_i = 0
    while running:
        sb_i = (sb_i + 1) % 6
        table1.hand(sb_i)


if __name__ == "__main__":
    main()

    pass
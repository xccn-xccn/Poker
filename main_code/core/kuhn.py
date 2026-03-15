import random
import os


class KuhnPlayer:
    def __init__(self, chips=100):
        self.chips = chips
        self.card = None
        self.round_invested = 0
        # self.action = None


import random


class KuhnBot(KuhnPlayer):

    # Load strategy
    root = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(root, "kuhn", "strategy.txt")) as t:

        strategy = eval(t.read())

    def get_action(self, table, player_i):

        player = table.players[player_i]

        strength = table.card_to_strength(player.card)

        history = "".join("p" if a == 0 else "b" for a in table.history)

        key = strength + history

        probs = self.strategy[key]

        r = random.random()

        if r < probs[0]:
            return 0
        else:
            return 1


class KuhnTable:

    def __init__(self, deck_size: int = 3):

        self.players = [KuhnBot(), KuhnPlayer()]
        self.deck = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"][
            :deck_size
        ]

        self.running = False
        self.starting_player = 1

        self.history = []
        self.pot = 0

        self.antes = 1

    def start_hand(self):

        random.shuffle(self.deck)

        self.history = []
        self.pot = 0
        self.running = True

        for i, p in enumerate(self.players):
            p.card = self.deck[i]
            p.chips -= self.antes
            p.round_invested = 1
            self.pot += self.antes

        self.current_player = self.starting_player = 1 - self.starting_player

    def _valid_move(self, action):
        """Returns if an action is valid"""

        return action in (0, 1)

    @staticmethod
    def card_to_strength(card: str) -> str:
        """Converts a card string to the number used in strategy dictionary"""

        if card in "TJQKA":
            card = {"T": 10, "J": 11, "Q": 12, "K": 13, "A": 14}[card]

        return str(int(card) - 2)

    def single_move(self, action) -> None | bool:
        """Applys an action for the current player

        Returns None if the action was invalid or a boolean to indicate if the hand ended
        """
        if not self.running:
            return

        if not self._valid_move(action):
            return

        player = self.players[self.current_player]

        if action == 1:
            player.chips -= 1
            player.round_invested += 1
            self.pot += 1

        print(player.round_invested, "invested")
        self.history.append(action)
        self.current_player = 1 - self.current_player

        if self._is_terminal():
            print("terminal")
            self._end_hand()
            self.running = False
            return True

        return False

    def _is_terminal(self):
        """Returns if the hand has ended"""

        print(self.history[-2:])
        return len(self.history) >= 2 and self.history[-2:] != [0, 1]

    def _end_hand(self):
        """Distributes pot to the winner of the hand"""

        h = self.history

        if h == [1, 0]:
            winner = 0

        elif h == [0, 1, 0]:
            winner = 1

        else:
            winner = self._showdown()

        self.players[winner].chips += self.pot
        self.running = False

    def _showdown(self) -> int:
        """Returns the index of the player with the strongest hand"""

        return int(
            self.card_to_strength(self.players[0].card)
            < self.card_to_strength(self.players[1].card)
        )

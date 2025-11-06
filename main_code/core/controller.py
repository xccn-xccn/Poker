"""
GUI should only call these methods

    controller.start_hand()          → start a new round
    controller.perform_action(a, val)  → player performs action (fold, call, raise)
    controller.update()              → Makes a bot move or if the current player cannot make a move, skips their turn
    controller.get_state()           → return dict of data for GUI rendering
"""

from core.poker import Table, Human, Bot, start


class GameController:
    def __init__(self):
        self.create_table()
        # TODO why is next used should probably be a list
        # self.human_player_id = next(
        #     p.id for p in self.table.players if isinstance(p, Human)
        # )

    def create_table(self):
        self.table = start() if callable(start) else Table()

    def start_hand(self):
        self.table.start_hand()

    def perform_action(self, action: int, amount: int = 0):  # action probably int
        # what if it's not human player move
        # TODO needs to ensure start_move is called before
        self.table.single_move(action, amount)

    def _action_str(self, num):
        return []

    def update(self):
        if not self.table.running:
            return
        cont, end = self.table.start_move()
        if cont:
            player = self.table.current_player
            if isinstance(player, Bot):
                move = player.get_action(self.table)
                end = self.table.single_move(move)
        if (
            end
        ):  # NOTE doesn't call end_round within end_move to allow gui to display stuff
            # TODO allow gui to display stuff maybe create a pygame event
            self.table.end_round()

    def _get_cards(self, player):
        if player.fold:
            return []
        if (
            isinstance(player, Human)
            or self.table.r >= self.table.skip_round
            or self.table.players_remaining > 1
            and self.table.running == False
        ):
            return player.hole_cards
        return ["card_back"] * 2

    def _get_poss_actions(self, player):
        return [
            (
                "Check"
                if not self.table.running
                or player.round_invested == self.table.last_bet
                else "Call"
            ),
            "Bet" if not self.table.running or not self.table.last_bet else "Raise",
        ]

    def _get_profile_picture(self, i):
        return ['nature', 'bot', 'calvin', 'daniel_n', 'elliot', 'teddy'][i]

    def _get_action(self, player):
        action = player.action

        if action == None:
            return ""
        if action == 1:
            return "Fold"
        if action == 2:
            return "Call" if player.extra else "Check"
        else:
            word = (
                "All In"
                if player.chips == 0
                else "Bet" if self.table.bet_count < 2 else "Raise"
            )
            return f"{word} {player.extra}"

    def get_state(self):
        state = {
            "players": [
                {
                    "chips": p.chips,
                    "folded": p.fold,
                    "hole_cards": self._get_cards(p),
                    "action": self._get_action(p),
                    "round_invested": p.round_invested,
                    "seat": i,  # TODO poss change
                    "position_name": p.position_name,
                    "poss_actions": self._get_poss_actions(p),
                    "profile_picture": self._get_profile_picture(i),
                }
                for i, p in enumerate(self.table.players)
            ],
            "community": self.table.community,
            "pot": self.table.get_pot() if self.table.running else 0,
            "running": self.table.running,
            "round": self.table.r,
            "user_i": next(
                i for i, p in enumerate(self.table.players) if isinstance(p, Human)
            ),
            "new_player": False,
        }

        return state


class OnlineController:
    pass

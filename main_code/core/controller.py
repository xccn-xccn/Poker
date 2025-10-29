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
        self.table.single_move(({"fold": 1, "call": 2, "raise": 3}[action], amount))

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

    def get_cards(self, player):
        if player.fold:
            return None
        if (
            isinstance(player, Human)
            or self.table.r >= self.table.skip_round
            or self.table.players_remaining > 1
            and self.table.running == False
        ):
            return player.hole_cards
        return []

    def get_actions(self, player):
        return [
            (
                "Check"
                if not self.table.running
                or player.round_invested == self.table.last_bet
                else "Call"
            ),
            "Bet" if not self.table.running or not self.table.last_bet else "Raise",
        ]

    def get_state(self):
        state = {
            "players": [
                {
                    "chips": p.chips,
                    "folded": p.fold,
                    "hole_cards": self.get_cards(p),
                    "action": p.action,
                    "round_invested": p.round_invested,
                    "seat": i,  # TODO poss change
                    "position_name": p.position_name,
                    "actions": self.get_actions(p),
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

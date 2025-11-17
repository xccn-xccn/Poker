"""
GUI should only call these methods

    controller.start_hand()          → start a new round
    controller.perform_action(a, val)  → player performs action (fold, call, raise)
    controller.update()              → Makes a bot move or if the current player cannot make a move, skips their turn
    controller.get_state()           → return dict of data for GUI rendering
"""

from core.poker import Table, Human, Bot, start
import socketio
import threading

# TODO remove uneeded default state?
# Slider should reset on succesful actions


class OfflineController:
    def __init__(self, testing: int = False):
        self.create_table()
        self.testing = testing

        self.set_state()

    def create_table(self):
        self.table = start() if callable(start) else Table()

    def start_hand(self):
        self.table.start_hand()
        self._process_system_actions(end=False)

    def perform_action(self, action: int, amount: int = 0):
        """True/False if round end None if move was invalid"""
        if not self.table.running or not isinstance(self.table.current_player, Human):
            return
        if not self.table.can_move():
            raise Exception(
                "Current player cannot make a move but this means their move should be skipped"
            )
        if self.table.can_move():
            end_valid = self.table.single_move((action, amount))

        if end_valid == None:
            print(f"User made an invalid action {action, amount}")
            return

        self.set_state()
        # SLEEP

        self._process_system_actions(end_valid)
        return end_valid

    def _single_auto_action(self):
        if self.table.can_move():
            player = self.table.current_player
            if isinstance(player, Bot):
                move = player.get_action(self.table)
                return self.table.single_move(move)
            elif self.testing:
                return self.table.single_move((1, 0))
        else:
            return self.table.end_move()

    def _process_system_actions(self, end=False):

        cont = True
        while self.table.running and cont:
            if end:
                self.table.end_round()
                end = False
            else:
                end = self._single_auto_action()

            if end == None:
                cont = False

            self.set_state()
            # SLEEP

    # State related methods
    def _get_cards(self, player):
        if player.fold or player.inactive:
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
        return ["nature", "bot", "calvin", "daniel_n", "elliot", "teddy"][i]

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
            return f"{word} {player.round_invested}"

    def set_state(self):
        self.state = {
            "players": [
                {
                    "chips": p.chips,
                    "folded": p.fold,
                    "hole_cards": self._get_cards(p),
                    "action": self._get_action(p),
                    "round_invested": p.round_invested,
                    "seat": i,
                    "position_name": p.position_name,
                    "poss_actions": self._get_poss_actions(p),
                    "profile_picture": self._get_profile_picture(i),
                }
                for i, p in enumerate(self.table.players)
                if p is not None
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

    def get_state(self):
        return self.state


class OnlineController:
    """
    This controller doesn't run any game logic.
    It just passes messages to/from the server.
    The GUI (GameWindow) doesn't know the difference.
    """

    def __init__(self, is_host=False, host_ip=None):
        self.sio = socketio.Client()
        self.server_url = f'http://{host_ip or "localhost"}:5000'

        # This will hold the game state sent by the server
        # TODO check if needed
        self.state = {
            "players": [
                {
                    "chips": 0,
                    "folded": True,
                    "hole_cards": [],
                    "action": "",
                    "round_invested": 0,
                    "seat": 0,  # TODO poss change
                    "position_name": "",
                    "poss_actions": ["Check", "Bet"],
                    "profile_picture": "nature",
                }
            ],
            "community": [],
            "pot": 0,
            "running": False,
            "user_i": 0,
            "new_player": False,
        }
        self.lock = threading.Lock()  # For thread-safe state updates

        self._register_handlers()
        self._connect()

    def _register_handlers(self):
        """Sets up the functions to call when messages arrive."""

        @self.sio.on("connect")
        def on_connect():
            print(f"Connected to server at {self.server_url}")

            print("Sending 'join_game' request...")
            self.sio.emit("join_game", {"chips": 2000})

        @self.sio.on("disconnect")
        def on_disconnect():
            print("Disconnected from server.")

        @self.sio.on("game_update")
        def on_game_update(data):
            """Saves the game state sent by the server"""
            with self.lock:
                self.state = data

            print(f"got state {data}")

    def _connect(self):
        """Tries to connect to the server."""
        try:
            self.sio.connect(self.server_url)
        except socketio.exceptions.ConnectionError as e:
            print(f"Failed to connect to server: {e}")

    def start_hand(self):
        print("Requesting new hand...")
        self.sio.emit("request_start_hand", {})

    def perform_action(self, action: int, amount: int = 0):
        """Called when 'Fold', 'Check', 'Bet' is clicked."""
        print(f"Sending action {action} ({amount}) to server...")
        self.sio.emit("request_action", {"action": action, "amount": amount})

    def get_state(self):
        with self.lock:
            return self.state

    def __del__(self):
        """Clean up the connection when this object is destroyed."""
        if self.sio.connected:
            self.sio.disconnect()

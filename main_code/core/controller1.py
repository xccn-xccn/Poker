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

# --- Offline Controller ---
# (This is your original class, unchanged)
class GameController:
    def __init__(self):
        self.create_table()

    def create_table(self):
        self.table = start() if callable(start) else Table()

    def start_hand(self):
        self.table.start_hand()

    def perform_action(self, action: int, amount: int = 0):
        """True/False if round end None if move was invalid"""
        if not self.table.running or not isinstance(self.table.current_player, Human):
            return 
        if self.table.can_move():
            end = self.table.single_move((action, amount))
        else:
            end = self.table.end_move()

        return end

    def end_round(self):
        self.table.end_round()

    def update(self):
        """Makes a bot move or skips the next players turn when appropriate"""
        if not self.table.running:
            return
        if self.table.can_move():
            player = self.table.current_player
            if isinstance(player, Bot):
                move = player.get_action(self.table)
                end = self.table.single_move(move)
            else:
                return
        else:
            end = self.table.end_move()

        return end
    
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


# --- NEW Online Controller ---

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
        self.state = {"players": [], "community": [], "pot": 0, "running": False, "user_i": 0} 
        self.lock = threading.Lock() # For thread-safe state updates

        self._register_handlers()
        self._connect()

    def _register_handlers(self):
        """Sets up the functions to call when messages arrive."""
        
        @self.sio.on('connect')
        def on_connect():
            print(f"Connected to server at {self.server_url}")
            # NEW: After connecting, we must ask to join a game
            print("Sending 'join_game' request...")
            self.sio.emit('join_game')

        @self.sio.on('disconnect')
        def on_disconnect():
            print("Disconnected from server.")

        @self.sio.on('game_update')
        def on_game_update(data):
            """
            This is the most important function.
            The server sent a new game state. We just save it.
            The GUI will ask for it in its next update().
            """
            # print("Received game update")
            with self.lock:
                self.state = data

    def _connect(self):
        """Tries to connect to the server."""
        try:
            self.sio.connect(self.server_url)
        except socketio.exceptions.ConnectionError as e:
            print(f"Failed to connect to server: {e}")
            # The GUI will get an empty state dict and show a blank table
            self.state = {"players": [], "community": [], "pot": 0, "running": False, "user_i": 0}

    # --- Methods called by GameWindow ---
    # (These now just send messages)
    
    def start_hand(self):
        """Called when 'Deal' is clicked."""
        print("Requesting new hand...")
        self.sio.emit('request_start_hand', {})

    def perform_action(self, action: int, amount: int = 0):
        """Called when 'Fold', 'Check', 'Bet' is clicked."""
        print(f"Sending action {action} ({amount}) to server...")
        self.sio.emit('request_action', {'action': action, 'amount': amount})
        
        # We return None because the server's response will
        # come via 'game_update' later. The GUI is built
        # to handle this (it won't freeze).
        return None

    def end_round(self):
        """
        The client-side timer calls this. We don't need to
        tell the server anything, the server already knows
        the round ended and is just waiting for 'start_hand'.
        """
        print("Client-side round end timer finished.")

    def update(self):
        """
        Bots are run on the server, so the client's
        update() method does nothing.
        """
        return None
    
    def get_state(self):
        """
        Called 60x/sec by the GUI.
        We just return the last state we received from the server.
        """
        with self.lock:
            return self.state

    def __del__(self):
        """Clean up the connection when this object is destroyed."""
        if self.sio.connected:
            self.sio.disconnect()
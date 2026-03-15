"""
GUI should only call these methods:
    controller.start_hand() -> start a new round
    controller.perform_action(action, amount) -> player performs action (fold, call, raise)
"""

from abc import ABC
from copy import deepcopy
from core.poker import Table, Human, Bot, start
from core.kuhn import KuhnTable, KuhnBot
from typing import Callable
import socketio
import threading
import time

# TODO remove uneeded default state?
# Slider should reset on succesful actions


class ControllerBase(ABC):
    def __init__(self, on_state_change: None | Callable = None):
        super().__init__()
        self.on_state_change = on_state_change

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
                    "round_invested": 0,
                }
            ],
            "community": [],
            "pot": 0,
            "running": False,
            "user_i": 0,
            "new_player": False,
            "round": 0,
            "new_round": False,
            "bb": 20,
        }

    def set_state_callback(self, on_state_change: None | Callable) -> None:
        self.on_state_change = on_state_change
        self.update_state()


# Could add an additional class
class OfflineController(ControllerBase):
    def __init__(self, testing: int = False, on_state_change: None | Callable = None):
        super().__init__(on_state_change)
        self.testing = testing

        print("testing", self.testing)
        self.create_table()
        self.auto_thread_running = False

        # self.on_state_change: None | function = on_state_change

    def create_table(self):
        self.table = start() if callable(start) and self.testing != "human" else Table()

        if self.testing == "human":
            for r in range(6):
                self.table.add_new_player()

    def start_hand(self):
        self.table.start_hand()
        self.update_state(round_end=True)

        if not self.auto_thread_running:
            self.start_systems_thread()

    def start_systems_thread(self, end_valid=False):
        t = threading.Thread(target=self._process_system_actions, args=(end_valid,))
        t.daemon = True
        self.auto_thread_running = True
        t.start()

    def perform_action(self, action: int, amount: int = 0):
        """True/False if round end, None if move was invalid"""
        if (
            not self.table.running
            or not isinstance(self.table.current_player, Human)
            or self.auto_thread_running == True
        ):
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

        self.update_state()

        self.start_systems_thread(end_valid)

        return end_valid

    def _single_auto_action(self) -> tuple[None, bool]:
        if self.table.can_move():
            player = self.table.current_player
            if isinstance(player, Bot):
                move = player.get_action(self.table)
                return self.table.single_move(move), True
            elif self.testing and self.testing[0] == "t":
                return self.table.single_move((1, 0)), False
        else:
            return self.table.end_move(), False

        return None, False

    def _process_system_actions(self, round_end=False):
        try:
            cont = True
            while self.table.running and cont:

                old_end = False
                start_time = time.time()
                if round_end:
                    self.table.start_round()
                    old_end = True
                    round_end = False
                    full_pause = True
                else:
                    round_end, full_pause = self._single_auto_action()

                if round_end is None:
                    cont = False

                if not (
                    self.testing and len(self.testing) >= 2 and self.testing[1] in "02"
                ):
                    elapsed = time.time() - start_time
                    sleep_time = max(0, 0.5 if full_pause else 0.1 - elapsed)

                    if self.state["players"][self.state["user_i"]]["folded"]:
                        sleep_time /= 2

                    time.sleep(sleep_time)
                # self.update_state(round_end=bool(round_end or old_end))
                self.update_state(round_end=bool(old_end))

        finally:
            self.auto_thread_running = False

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

    def _get_profile_picture(self, i) -> str:
        return ["jerry", "bot", "calvin2", "dog", "elliot", "teddy2"][i]

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
                if player.all_in 
                else "Bet" if self.table.bet_count < 2 else "Raise"
            )
            return f"{word} {player.round_invested}"

    def update_state(self, round_end=False):
        """Updates state and calls the traceback (emits) self.on_state_change"""
        self.set_state(round_end)
        self.on_state_change(deepcopy(self.state))

    def set_state(self, round_end=False):
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
            # "pot": self.table.get_pot() if self.table.running else 0,
            "pot": self.table.get_pot(),
            "running": self.table.running,
            "round": self.table.r,
            "new_round": round_end,
            "user_i": next(
                i for i, p in enumerate(self.table.players) if isinstance(p, Human)
            ),
            "new_player": False,
            "bb": self.table.blinds[1],
        }

    def get_state(self):
        return deepcopy(self.state)


class KuhnController(ControllerBase):

    def __init__(self, on_state_change=None):

        super().__init__(on_state_change)

        self.table = KuhnTable(13)
        self.bot = KuhnBot()
        self.auto_thread_running = False

        self.user_i = 0
        self.bot_i = 1

    def start_hand(self):

        self.table.start_hand()
        self.update_state(round_end=True)

        if not self.auto_thread_running:
            self.start_systems_thread()

    def perform_action(self, action: int, amount: int = 0):
        action -= 2
        if (
            not self.table.running
            or self.table.current_player != self.user_i
            or self.auto_thread_running
        ):
            return

        end = self.table.single_move(action)

        if end is None:
            print("Invalid user action")
            return

        self.update_state(round_end=bool(end))
        self.start_systems_thread()

        return end

    def start_systems_thread(self):

        t = threading.Thread(target=self._process_system_actions)
        t.daemon = True
        self.auto_thread_running = True
        t.start()

    def _process_system_actions(self):

        try:
            while self.table.running:

                if self.table.current_player == self.bot_i:

                    time.sleep(0.5)

                    action = self.bot.get_action(self.table, self.bot_i)
                    end = self.table.single_move(action)

                    self.update_state(round_end=bool(end))
                    if end:
                        break

                else:
                    break

        finally:
            self.auto_thread_running = False

    def _get_cards(self, i):

        player = self.table.players[i]

        if not player.card:
            return []

        if not self.table.running or i == self.user_i:
            return [player.card + "H"]

        return ["card_back"]

    def _get_action(self, i: int) -> str:
        """Returns the player's last action"""
        if not self.table.history:
            return ""

        last_player = (self.table.current_player - 1) % 2
        history_i = -2 if last_player != i else -1

        if len(self.table.history) < -history_i:
            return ""

        action = self.table.history[history_i]

        return "Pass" if action == 0 else "Bet"

    def set_state(self, round_end=False):
        self.state = {
            "players": [
                {
                    "chips": p.chips,
                    "folded": False,
                    "hole_cards": self._get_cards(i),
                    "action": self._get_action(i),
                    "round_invested": p.round_invested,
                    "seat": i,
                    "position_name": "",
                    "poss_actions": ["Pass", "Bet"],
                    "profile_picture": "jerry" if i == self.user_i else "bot",
                }
                for i, p in enumerate(self.table.players)
            ],
            "community": [],
            "pot": self.table.pot,
            "running": self.table.running,
            "round": 0,
            "new_round": round_end,
            "user_i": self.user_i,
            "new_player": False,
            "bb": 1,
        }

    def update_state(self, round_end=False):
        """Updates state and calls the traceback (emits) self.on_state_change"""
        self.set_state(round_end)

        print(self.state)
        self.on_state_change(deepcopy(self.state))


class OnlineController(ControllerBase):
    def __init__(
        self, is_host=False, host_ip=None, on_state_change: None | Callable = None
    ):
        super().__init__(on_state_change=on_state_change)

        self.sio = socketio.Client()
        self.server_url = f'http://{host_ip or "localhost"}:5000'
        self.lock = threading.Lock()  # thread safe state updates

        self._register_handlers()
        self._connect()

    def _register_handlers(self):
        """Set up handlers for when server emits messages"""

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

            if self.on_state_change:
                self.on_state_change(deepcopy(data))

            print(f"got state {data}")

    def update_state(self):
        print("update state")
        self.on_state_change(self.state)

    def _connect(self):
        """Tries to connect to the server."""
        self.sio.connect(self.server_url)

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

    # def set_state_callback(self, on_state_change):
    #     print('callback set \n')
    #     self.on_state_change = on_state_change

    def __del__(self):
        """Clean up connection when this is destroyed"""
        if self.sio.connected:
            self.sio.disconnect()

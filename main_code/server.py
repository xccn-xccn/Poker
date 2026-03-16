from core.poker import Table, Human, Bot
import eventlet

eventlet.monkey_patch()


from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import Flask, request


# TODO
# Optimize making state
# Add removing players
class GameRoom:
    """Represents a single poker table"""

    def __init__(self):
        self.table: Table = Table()
        self.sid_seat: dict[int:int] = {}
        self.full: bool = False

    def add_player(self, sid: int, data: dict):
        seat_i = self.table.add_new_player(data["chips"])
        self.sid_seat[sid] = seat_i

        self.set_full()
        self.emit_state(new=True)

    def remove_player(self, sid: int):
        # TODO test
        player_i = self.sid_seat[sid]
        if (
            self.table.running
            and self.table.players[player_i] == self.table.current_player
        ):
            self.player_action(sid, {"action": 1, "amount": 0})

        self.table.remove_player(player_i)
        self.full = False
        del self.sid_seat[sid]

        self.emit_state()

    def start_hand(self):
        if self.table.running or len([x for x in self.table.players if x]) <= 1:
            return

        self.table.start_hand()
        self._process_system_actions(end=False)

    def _single_auto_action(self):
        """Runs a bot move or skips the current player's turn if they cannot make an action e.g has no chips remaining"""
        if self.table.can_move():
            player = self.table.current_player
            if isinstance(player, Bot):
                move = player.get_action(self.table)
                return self.table.single_move(move)
        else:
            return self.table.end_move()

    def _process_system_actions(self, end=False):

        cont = True
        while self.table.running and cont:

            old_end = False
            if end:
                self.table.start_round()
                end = False
                old_end = True
            else:
                end = self._single_auto_action()

            if end == None:
                cont = False

            self.emit_state(new_round=(old_end))
            eventlet.sleep(1)

    def player_action(self, sid: int, data: int):
        if sid not in self.sid_seat:
            raise Exception(sid, self.sid_seat)

        user = self.table.players[self.sid_seat[sid]]
        if not self.table.running or user != self.table.current_player:
            return

        if not self.table.can_move():
            raise Exception(
                "Current player cannot make a move but this means their move should be skipped"
            )

        end_valid = self.table.single_move((data["action"], data["amount"]))

        if end_valid == None:
            print(f"User {sid} made an invalid action {data}")
            return

        self.emit_state()
        eventlet.sleep(1)

        self._process_system_actions(end_valid)

        return True

    # State related methods

    def emit_state(self, new=False, new_round=False):
        """Sends state to each user in the room"""
        print("player to seat", self.sid_seat.items())
        for sid, seat in self.sid_seat.items():
            player = self.table.players[seat]
            if not isinstance(player, Human):
                continue
            socketio.emit(
                "game_update",
                self.get_specific_state(player, seat, new=new, new_round=new_round),
                to=sid,
            )

    def _get_cards(self, other_player, user_player):
        if other_player.fold or other_player.inactive:
            return []
        if (
            other_player == user_player
            or self.table.r >= self.table.skip_round
            or self.table.players_remaining > 1
            and self.table.running == False
        ):
            return other_player.hole_cards
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

    def get_specific_state(
        self, user_player: Human, seat: int, new=False, new_round=False
    ):
        """Returns the state for a specific player,
        insuring that they only get information they should access"""

        user_i = len([x for i, x in enumerate(self.table.players) if x and i < seat])
        state = {
            "players": [
                {
                    "chips": p.chips,
                    "folded": p.fold,
                    "hole_cards": self._get_cards(p, user_player),
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
            "new_round": new_round,
            "user_i": user_i,
            "new_player": new,
            "bb": self.table.blinds[1],
        }

        return state

    def set_full(self):
        self.full = self.table.players.count(None) <= 4


class ServerManager:
    """Manages player connections"""

    def __init__(self):
        # room_id to GameRoom instance
        self.rooms: dict[int:GameRoom] = {}

        # sid to room_id
        self.sid_to_room: dict[int:int] = {}

    def create_new_room(self) -> tuple[GameRoom | int]:
        room = GameRoom()
        room_id = str(id(room))
        self.rooms[room_id] = room
        print(f"New game room created: {room_id}")

        return room, room_id

    def find_or_create_room(self) -> tuple[GameRoom | int]:
        for room_id, game_room in self.rooms.items():

            if not game_room.full:
                return game_room, room_id

        game_room, room_id = self.create_new_room()
        return game_room, room_id

    def handle_join_game(self, player_sid: int, data: dict):
        game_room, room_id = self.find_or_create_room()

        game_room.add_player(player_sid, data)
        self.sid_to_room[player_sid] = room_id

        join_room(room_id, sid=player_sid)

        print(f"Human player {player_sid} joined room {room_id}")

    def handle_disconnect(self, sid):
        if sid in self.sid_to_room:
            room_id = self.sid_to_room.pop(sid)
            room = self.rooms[room_id]
            empty = room.remove_player(sid)
            leave_room(room_id)

            if empty:
                print(f"Room {room_id} is now empty. Deleting game.")
                del self.rooms[room_id]

            print(f"Human player {sid} disconnected from room {room_id}.")

            # socketio.emit("game_update", room.get_state(0, 0), room=room_id)

    def handle_start_hand(self, sid):
        if sid not in self.sid_to_room:
            return

        room_id = self.sid_to_room[sid]
        game_room = self.rooms[room_id]

        game_room.start_hand()

        print(f"Room {room_id}: Received request to start hand...")

    def handle_player_action(self, sid: int, data: int):
        if sid not in self.sid_to_room:
            return

        room_id = self.sid_to_room[sid]

        game_room = self.rooms[room_id]

        game_room.player_action(sid, data)

        print(f"Room {room_id}: Received action {data} sid {sid}")


app = Flask(__name__)
app.config["SECRET_KEY"] = "e281c3cbc82d9c62e4_change_for_production"
socketio = SocketIO(app)

manager = ServerManager()


@socketio.on("connect")
def handle_connect():
    """A new client connects."""
    sid = request.sid
    print(f"Client {sid} connected. Waiting for them to join a game.")


@socketio.on("join_game")
def handle_join_game(data: dict):
    """Routes the 'join_game' request to the manager."""
    manager.handle_join_game(request.sid, data)


@socketio.on("disconnect")
def handle_disconnect(data):
    """Routes the 'disconnect' event to the manager."""

    print(f"Handle disconnect data {data}")
    manager.handle_disconnect(request.sid)


@socketio.on("request_start_hand")
def handle_start_hand(data):
    """Routes the 'request_start_hand' event to the manager."""
    manager.handle_start_hand(request.sid)


@socketio.on("request_action")
def handle_player_action(data):
    """Routes the player's action to the manager."""
    manager.handle_player_action(request.sid, data)


if __name__ == "__main__":
    print("Starting Flask-SocketIO server at http://localhost:5000")
    socketio.run(app, host="0.0.0.0", port=5000)

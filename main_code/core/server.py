import eventlet

eventlet.monkey_patch()

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from core.poker import Table, Human, Bot, start


class GameRoom:
    """Represents a single poker table"""

    def __init__(self):
        self.table: Table = Table()
        self.sid_seat: dict[int:int] = {}
        self.full: bool = False

    def add_player(self, sid: int, data: dict):
        seat_i = self.table.add_new_player(data["chips"])
        self.sid_seat[sid] = seat_i

        self.full = None not in self.table.players

    def remove_player(self, sid: int):
        pass

    def get_state(self):
        pass

    def _emit_state(self):
        pass

    def _single_auto_action(self):
        if self.table.can_move():
            player = self.table.current_player
            if isinstance(player, Bot):
                move = player.get_action(self.table)
                return self.table.single_move(move)
        else:
            return self.table.end_move()

    def _process_system_actions(self, end):

        cont = True
        while self.table.running and cont:
            if end:
                self.table.end_round()
                end = False
            else:
                end = self._single_auto_action()

            if end == None:
                cont = False

            self._emit_state()
            eventlet.sleep(1)

    def player_action(self, sid: int, data: int):
        if sid not in self.sid_seat:
            raise Exception(sid, self.sid_seat)

        user = self.table.players[self.sid_seat[sid]]
        if not self.table.running or user != self.table.current_player:
            return

        if not self.table.can_move():
            raise Exception()

        end = self.table.single_move((data["action"], data["amount"]))

        if end == None:
            return

        self._emit_state()
        eventlet.sleep(1)

        self._process_system_actions(end)

        return True


class ServerManager:
    """Manages player connections."""

    def __init__(self):
        # room_id to GameRoom instance
        self.rooms: dict[int:GameRoom] = {}
        # sid to room_id
        self.sid_to_room: dict[int:int] = {}

    # --- Helper Functions (Private Methods) ---
    # These helpers now belong to the class and are used by get_state()

    # --- Connection/Room Methods (Called by the Socket.IO handlers) ---

    def create_new_game(self) -> tuple[GameRoom | int]:
        """Creates a new game table and adds it to the manager."""
        room = GameRoom()
        room_id = str(id(room))
        self.rooms[room_id] = room
        print(f"New game room created: {room_id}")

        return room, room_id

    def find_or_create_room(self) -> tuple[GameRoom | int]:
        """Finds an available game room with an empty seat, or creates a new one."""
        for room_id, game_room in self.rooms.items():

            if not game_room.full:
                return game_room, room_id

        game_room, room_id = self.create_new_game()
        return game_room, room_id

    def handle_join_game(self, player_sid: int, data: dict):
        """Handles a client requesting to join a game."""
        game_room, room_id = self.find_or_create_room()

        game_room.add_player(player_sid, data)
        self.sid_to_room[player_sid] = room_id

        join_room(room_id, sid=player_sid)

        print(f"Human player {player_sid} joined room {room_id}")

        # # Send the initial state back to the whole room
        # socketio.emit(
        #     "game_update", self.get_state(game_room, seat_index), room=room_id
        # )

    def handle_disconnect(self, sid):
        """Handles a client disconnecting."""

        if sid in self.sid_to_room:
            room_id = self.sid_to_room.pop(sid)
            room = self.rooms[room_id]
            empty = room.remove_player(sid)
            leave_room(room_id)

            if empty:
                print(f"Room {room_id} is now empty. Deleting game.")
                del self.rooms[room_id]

            print(f"Human player {sid} disconnected from room {room_id}.")

            socketio.emit("game_update", room.get_state(0, 0), room=room_id)

    def handle_start_hand(self, sid):
        """Handles a client requesting to start a new hand."""
        if sid not in self.sid_to_room:
            return

        mapping = self.sid_to_room[sid]
        room_id = mapping["room"]
        game_room = self.rooms.get(room_id)
        if not game_room:
            return

        print(f"Room {room_id}: Received request to start hand...")
        if not game_room.running:
            game_room.start_hand()
            self.run_bot_moves(game_room)  # Run bots until human turn

        # Broadcast the new state to everyone in the room
        socketio.emit(
            "game_update", self.get_state(game_room, mapping["seat"]), room=room_id
        )

    def handle_player_action(self, sid: int, data: int):
        """Handles a human player performing an action (fold, bet, call, raise)."""
        if sid not in self.sid_to_room:
            return

        room_id = self.sid_to_room[sid]
        
        game_room = self.rooms[room_id]

        #could return the result
        game_room.player_action(sid, data)


# --- App Setup ---
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret-donk-bet"
socketio = SocketIO(app)

# --- Instantiate the OO Manager ---
# This single instance manages all the games
manager = ServerManager()

# --- Socket.IO Event Handlers (Routing requests to the Manager) ---


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
def handle_disconnect():
    """Routes the 'disconnect' event to the manager."""
    manager.handle_disconnect(request.sid)


@socketio.on("request_start_hand")
def handle_start_hand(data):
    """Routes the 'request_start_hand' event to the manager."""
    manager.handle_start_hand(request.sid)


@socketio.on("request_action")
def handle_player_action(data):
    """Routes the player's action to the manager."""
    manager.handle_player_action(request.sid, data)


# --- Run Server ---
if __name__ == "__main__":
    print("Starting Flask-SocketIO server at http://localhost:5000")
    socketio.run(app, host="0.0.0.0", port=5000)

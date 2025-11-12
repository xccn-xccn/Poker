import eventlet
eventlet.monkey_patch()

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from core.poker import Table, Human, Bot, start


# --- App Setup ---
app = Flask(__name__)
app.config["SECRET_KEY"] = "your-very-secret-key!"
socketio = SocketIO(app)

# --- Server-Side Game Logic ---
active_games = {}  # Stores the game `Table` object for each room
player_to_room = {}  # Maps a player's sid to their room_name


def create_new_game():
    """Creates a new game table and adds it to the manager."""
    # We'll use the Table's object ID as a simple unique room name
    game_table = start() if callable(start) else Table()
    room_name = str(id(game_table))
    active_games[room_name] = game_table
    print(f"New game room created: {room_name}")
    return game_table, room_name


def find_or_create_game():
    """Finds an available game room with an empty seat, or creates a new one."""
    # Try to find a game with an empty human seat
    for room_name, game_table in active_games.items():
        # Find all Human seats that aren't taken
        human_seats = [
            i for i, p in enumerate(game_table.players) if isinstance(p, Human)
        ]
        taken_seats = [
            p.get("seat") for p in game_table.players if p.get("is_human_player")
        ]

        available_seats = [seat for seat in human_seats if seat not in taken_seats]
        if available_seats:
            return game_table, room_name, available_seats[0]

    # If no available games, create a new one
    game_table, room_name = create_new_game()
    # Find the first human seat
    human_seat_index = next(
        i for i, p in enumerate(game_table.players) if isinstance(p, Human)
    )
    return game_table, room_name, human_seat_index


def get_state(game_table, user_seat_index):
    """
    This is your exact get_state logic, now running on the server.
    """
    state = {
        "players": [
            {
                "chips": p.chips,
                "folded": p.fold,
                "hole_cards": _get_cards(p),
                "action": _get_action(p, game_table),
                "round_invested": p.round_invested,
                "seat": i,
                "position_name": p.position_name,
                "poss_actions": _get_poss_actions(p),
                "profile_picture": _get_profile_picture(i),
            }
            for i, p in enumerate(game_table.players)
        ],
        "community": game_table.community,
        "pot": game_table.get_pot() if game_table.running else 0,
        "running": game_table.running,
        "round": game_table.r,
        "user_i": user_seat_index,  # The GUI will follow this player
        "new_player": False,
    }
    return state


def run_bot_moves(game_table):
    """Handles bot turns automatically."""
    end_round = False
    while game_table.running and isinstance(game_table.current_player, Bot):
        if game_table.can_move():
            move = game_table.current_player.get_action(game_table)
            end_round = game_table.single_move(move)
        else:
            end_round = game_table.end_move()

        if end_round:
            break

    return end_round


# --- Helper functions copied from your GameController ---
def _get_cards(player, game_table):
    if player.fold:
        return []
    if (
        isinstance(player, Human)
        or game_table.r >= game_table.skip_round
        or game_table.players_remaining > 1
        and game_table.running == False
    ):
        return player.hole_cards
    return ["card_back"] * 2


def _get_poss_actions(player, game_table):
    return [
        (
            "Check"
            if not game_table.running or player.round_invested == game_table.last_bet
            else "Call"
        ),
        "Bet" if not game_table.running or not game_table.last_bet else "Raise",
    ]


def _get_profile_picture(i):
    return ["nature", "bot", "calvin", "daniel_n", "elliot", "teddy"][i]


def _get_action(player, game_table):
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
            else "Bet" if game_table.bet_count < 2 else "Raise"
        )
        return f"{word} {player.extra}"


# --- Socket.IO Event Handlers ---


@socketio.on("connect")
def handle_connect():
    """A new player connects. Just log it. They need to 'join_game' to play."""
    player_id = request.sid
    print(f"Client {player_id} connected. Waiting for them to join a game.")


@socketio.on("join_game")
def handle_join_game():
    """A new player wants to join a table."""
    player_id = request.sid

    # Find a game and a seat for this player
    game_table, room_name, seat_index = find_or_create_game()

    # Assign this player to the seat
    game_table.players[seat_index].is_human_player = True  # Mark the seat as taken

    # Store the mapping
    player_to_room[player_id] = {"room": room_name, "seat": seat_index}

    # Add the player to the SocketIO room
    join_room(room_name)

    print(f"Human player {player_id} joined room {room_name} at seat {seat_index}.")

    # Broadcast the new state TO THAT ROOM
    emit("game_update", get_state(game_table, seat_index), room=room_name)


@socketio.on("disconnect")
def handle_disconnect():
    player_id = request.sid
    if player_id in player_to_room:
        mapping = player_to_room.pop(player_id)
        room_name = mapping["room"]
        seat_index = mapping["seat"]

        print(
            f"Human player {player_id} (seat {seat_index}) disconnected from room {room_name}."
        )

        if room_name in active_games:
            game_table = active_games[room_name]
            # Mark the seat as available again
            game_table.players[seat_index].is_human_player = False
            # TODO: You could add logic here to fold the player

            # Tell everyone else in the room
            leave_room(room_name)
            emit(
                "game_update", get_state(game_table, 0), room=room_name
            )  # 0 is a default seat

            # Optional: Clean up empty games
            # ...
    else:
        print(f"Spectator {player_id} disconnected.")


@socketio.on("request_start_hand")
def handle_start_hand(data):
    """Client clicked 'Deal'."""
    player_id = request.sid
    if player_id not in player_to_room:
        return  # Only players can start

    mapping = player_to_room[player_id]
    room_name = mapping["room"]
    game_table = active_games.get(room_name)
    if not game_table:
        return

    print(f"Room {room_name}: Received request to start hand...")
    if not game_table.running:
        game_table.start_hand()
        # After starting, check if it's a bot's turn
        run_bot_moves(game_table)

    # Broadcast the new state TO THAT ROOM
    emit("game_update", get_state(game_table, 0), room=room_name)


@socketio.on("request_action")
def handle_player_action(data):
    """Client (Human) performed an action."""
    player_id = request.sid
    if player_id not in player_to_room:
        return  # Only players can act

    mapping = player_to_room[player_id]
    room_name = mapping["room"]
    seat = mapping["seat"]
    game_table = active_games.get(room_name)
    if not game_table:
        return

    if seat != game_table.current_player_i:
        print(
            f"Action from player {seat} received, but it's player {game_table.current_player_i}'s turn."
        )
        return  # Not this player's turn

    action = data.get("action")
    amount = data.get("amount")
    end_round = False

    if game_table.can_move():
        print(
            f"Room {room_name}: Processing action {action} ({amount}) from player {seat}..."
        )
        end_round = game_table.single_move((action, amount))
    else:
        end_round = game_table.end_move()

    if not end_round:
        # After human move, check for bot moves
        end_round = run_bot_moves(game_table)

    # If the round ended (e.g., showdown, or everyone folded)
    if end_round:
        print(f"Room {room_name}: Round has ended.")
        game_table.end_round()
        # We will show the result for a moment,
        # The client's GameWindow ROUND_END_EVENT timer will handle the pause.
        # The client will call `request_start_hand` when ready.

    # Broadcast the new state TO THAT ROOM
    emit("game_update", get_state(game_table, 0), room=room_name)


# --- Run Server ---
if __name__ == "__main__":
    print("Starting Flask-SocketIO server at http://localhost:5000")
    socketio.run(app, host="0.0.0.0", port=5000)

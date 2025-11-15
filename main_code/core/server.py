import eventlet 
eventlet.monkey_patch() 

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from core.poker import Table, Human, Bot, start

class GameServerManager:
    """Manages all active poker tables and player connections."""
    
    def __init__(self):
        # Stores the game `Table` object for each room (the single source of truth)
        self.active_games = {} 
        # Maps a player's session ID (sid) to their room_name and seat index
        self.player_to_room = {} 
    
    # --- Helper Functions (Private Methods) ---
    # These helpers now belong to the class and are used by get_state()

    def _get_cards(self, player, game_table):
        # Your existing logic for showing hole cards
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

    def _get_poss_actions(self, player, game_table):
        # Your existing logic for determining available actions
        return [
            (
                "Check"
                if not game_table.running
                or player.round_invested == game_table.last_bet
                else "Call"
            ),
            "Bet" if not game_table.running or not game_table.last_bet else "Raise",
        ]

    def _get_profile_picture(self, i):
        return ["nature", "bot", "calvin", "daniel_n", "elliot", "teddy"][i]

    def _get_action(self, player, game_table):
        # Your existing logic for formatting the action text
        action = player.action
        if action is None: return ""
        if action == 1: return "Fold"
        if action == 2: return "Call" if player.extra else "Check"
        else:
            word = ("All In" if player.chips == 0 else "Bet" if game_table.bet_count < 2 else "Raise")
            return f"{word} {player.extra}"

    # --- Core Game Logic Methods ---

    def run_bot_moves(self, game_table):
        """Handles bot turns automatically until a human or the end of the round."""
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

    def get_state(self, game_table, user_seat_index):
        """Creates a standardized game state dictionary to send to a specific client."""
        state = {
            "players": [
                {
                    "chips": p.chips,
                    "folded": p.fold,
                    "hole_cards": self._get_cards(p, game_table),
                    "action": self._get_action(p, game_table),
                    "round_invested": p.round_invested,
                    "seat": i,
                    "position_name": p.position_name,
                    "poss_actions": self._get_poss_actions(p, game_table),
                    "profile_picture": self._get_profile_picture(i),
                }
                for i, p in enumerate(game_table.players)
            ],
            "community": game_table.community,
            "pot": game_table.get_pot() if game_table.running else 0,
            "running": game_table.running,
            "round": game_table.r,
            "user_i": user_seat_index, # The GUI will follow this player
            "new_player": False,
        }
        return state

    # --- Connection/Room Methods (Called by the Socket.IO handlers) ---

    def create_new_game(self):
        """Creates a new game table and adds it to the manager."""
        game_table = Table()
        # Initialize the custom flag used for tracking taken seats
        room_id = str(id(game_table))
        self.active_games[room_id] = game_table
        print(f"New game room created: {room_id}")

        return game_table, room_id

    def find_or_create_game(self):
        """Finds an available game room with an empty seat, or creates a new one."""
        for room_id, game_table in self.active_games.items():
            
            if None in game_table.players:
                return game_table, room_id
            # for i, p in enumerate(game_table):
            #     if p == None:
            #         return game_table, room_name, i

        # If no available games create one
        game_table, room_id = self.create_new_game()
        return game_table, room_id

    def handle_join_game(self, player_sid: int, data: dict):
        """Handles a client requesting to join a game."""
        game_table, room_name = self.find_or_create_game()
        
        # Assign this player to the seat and update the table status
        seat_index = game_table.add_new_player(data["chips"])
        
        # Store the mapping
        self.player_to_room[player_sid] = {
            "room": room_name,
            "seat": seat_index
        }
        
        # Add the player to the SocketIO room
        join_room(room_name, sid=player_sid)
        
        print(f"Human player {player_sid} joined room {room_name} at seat {seat_index}.")
        
        # Send the initial state back to the whole room
        socketio.emit('game_update', self.get_state(game_table, seat_index), room=room_name)

    def handle_disconnect(self, player_id):
        """Handles a client disconnecting."""
        if player_id in self.player_to_room:
            mapping = self.player_to_room.pop(player_id)
            room_name = mapping["room"]
            seat_index = mapping["seat"]
            
            print(f"Human player {player_id} (seat {seat_index}) disconnected from room {room_name}.")
            
            if room_name in self.active_games:
                game_table = self.active_games[room_name]
                
                # Mark the seat as available again
                if seat_index < len(game_table.players):
                    game_table.players[seat_index].is_human_player = False
                
                # Clean up empty games (removes the table if no humans are left)
                human_players_left = sum(
                    1 for p in game_table.players if getattr(p, 'is_human_player', False)
                )
                if human_players_left == 0:
                    print(f"Room {room_name} is now empty. Deleting game.")
                    del self.active_games[room_name]
                    return

                # Notify remaining players
                leave_room(room_name)
                # Send a general update 
                socketio.emit('game_update', self.get_state(game_table, 0), room=room_name)
        else:
            print(f"Spectator {player_id} disconnected.")

    def handle_start_hand(self, player_id):
        """Handles a client requesting to start a new hand."""
        if player_id not in self.player_to_room: return 
        
        mapping = self.player_to_room[player_id]
        room_name = mapping["room"]
        game_table = self.active_games.get(room_name)
        if not game_table: return

        print(f"Room {room_name}: Received request to start hand...")
        if not game_table.running:
            game_table.start_hand()
            self.run_bot_moves(game_table) # Run bots until human turn
        
        # Broadcast the new state to everyone in the room
        socketio.emit('game_update', self.get_state(game_table, mapping["seat"]), room=room_name)

    def handle_player_action(self, player_id, data):
        """Handles a human player performing an action (fold, bet, call, raise)."""
        if player_id not in self.player_to_room: return
        
        mapping = self.player_to_room[player_id]
        room_name = mapping["room"]
        seat = mapping["seat"]
        game_table = self.active_games.get(room_name)
        if not game_table: return
        
        # Security check: Is it this player's turn?
        if seat != game_table.current_player_i:
            return 

        action = data.get('action')
        amount = data.get('amount')
        end_round = False
        
        if game_table.can_move():
            print(f"Room {room_name}: Processing action {action} ({amount}) from player {seat}...")
            end_round = game_table.single_move((action, amount))
        else:
            end_round = game_table.end_move()

        if not end_round:
            end_round = self.run_bot_moves(game_table) # Run bots after human move

        # If the round ended (e.g., showdown)
        if end_round:
            print(f"Room {room_name}: Round has ended.")
            game_table.end_round()

        # Broadcast the new state to everyone in the room
        socketio.emit('game_update', self.get_state(game_table, mapping["seat"]), room=room_name)


# --- App Setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-donk-bet'
socketio = SocketIO(app)

# --- Instantiate the OO Manager ---
# This single instance manages all the games
manager = GameServerManager()

# --- Socket.IO Event Handlers (Routing requests to the Manager) ---

@socketio.on('connect')
def handle_connect():
    """A new client connects."""
    player_id = request.sid
    print(f'Client {player_id} connected. Waiting for them to join a game.')

@socketio.on('join_game')
def handle_join_game(data: dict):
    """Routes the 'join_game' request to the manager."""
    manager.handle_join_game(request.sid, data)

@socketio.on('disconnect')
def handle_disconnect():
    """Routes the 'disconnect' event to the manager."""
    manager.handle_disconnect(request.sid)

@socketio.on('request_start_hand')
def handle_start_hand(data):
    """Routes the 'request_start_hand' event to the manager."""
    manager.handle_start_hand(request.sid)

@socketio.on('request_action')
def handle_player_action(data):
    """Routes the player's action to the manager."""
    manager.handle_player_action(request.sid, data)

# --- Run Server ---
if __name__ == '__main__':
    print("Starting Flask-SocketIO server at http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000)
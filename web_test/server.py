import eventlet # MUST be imported and patched before other libraries
eventlet.monkey_patch()

from flask import Flask, render_template_string, request # Added 'request' for event handlers
from flask_socketio import SocketIO, emit, join_room, leave_room

# A simple in-memory log of messages (optional, just to show history)
messages = []

# --- FLASK AND SOCKETIO INITIALIZATION ---
# These lines MUST come before any use of @app.route or @socketio.on
app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret!'
socketio = SocketIO(app)

# --- Standard HTTP Route (for the Web Client) ---
@app.route('/')
def index():
    """Serves a basic HTML chat client."""
    # Use a basic template string here to include the necessary JavaScript
    return render_template_string(
        """
        <!doctype html>
        <title>SocketIO Chat</title>
        <h1>Simple SocketIO Chat</h1>
        <div id="messages" style="height: 200px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px;"></div>
        <input type="text" id="username" placeholder="Enter your name" value="WebUser">
        <input type="text" id="msg_input" placeholder="Type a message">
        <button onclick="sendMessage()">Send</button>
        <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
        <script>
            const socket = io();
            const messagesDiv = document.getElementById('messages');
            const msgInput = document.getElementById('msg_input');
            const usernameInput = document.getElementById('username');

            socket.on('connect', () => {
                messagesDiv.innerHTML += '<p style="color: green;">Connected to server!</p>';
            });

            socket.on('server_broadcast', (data) => {
                messagesDiv.innerHTML += `<p><strong>${data.user}:</strong> ${data.text}</p>`;
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            });

            function sendMessage() {
                const text = msgInput.value;
                if (text) {
                    // Send an event named 'client_message' with the data
                    socket.emit('client_message', {
                        user: usernameInput.value || 'WebUser',
                        text: text
                    });
                    msgInput.value = '';
                }
            }
        </script>
        """
    )


# --- SocketIO Event Handlers ---

@socketio.on('connect')
def handle_connect():
    """Called when a client first connects (via Python or Web)."""
    # 'request.sid' is the unique session ID of the connected client
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Called when a client disconnects."""
    print(f"Client disconnected: {request.sid}")

@socketio.on('client_message')
def handle_client_message(data):
    """
    Handles an incoming message event named 'client_message'.
    'data' is the JSON payload sent by the client.
    """
    user = data.get('user', 'Anonymous')
    text = data.get('text', 'No Text')
    
    print(f"Received from {user} ({request.sid}): {text}")
    messages.append({'user': user, 'text': text})
    
    # Send the message to ALL connected clients (including the sender)
    # The event name 'server_broadcast' is what the clients listen for.
    emit('server_broadcast', {'user': user, 'text': text}, broadcast=True)


if __name__ == '__main__':
    print("Starting Flask-SocketIO Chat Server at http://localhost:5000")
    # Use the socketio.run wrapper instead of app.run
    socketio.run(app, host='0.0.0.0', port=5000)
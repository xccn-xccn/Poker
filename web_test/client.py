import socketio
import threading
import time

# --- Setup Client ---
sio = socketio.Client()
USERNAME = "PythonClient" 

# --- Event Handlers (Decorators) ---

@sio.event
def connect():
    """Called when the connection is established."""
    print("--- CONNECTED ---")
    print("Sending initial message to server...")
    # Send an event named 'client_message'
    sio.emit('client_message', {
        'user': USERNAME,
        'text': "Hello world, I am a Python client!"
    })

@sio.event
def disconnect():
    """Called when the client loses connection."""
    print("--- DISCONNECTED ---")

@sio.on('server_broadcast')
def on_broadcast(data):
    """
    Called when the server emits an event named 'server_broadcast'.
    This is how you receive messages from other users/the server.
    """
    print(f"[RECV] {data['user']}: {data['text']}")

# --- Main Logic ---

def run_client():
    """Connects and runs the client in the main thread."""
    try:
        sio.connect('http://localhost:5000')
    except socketio.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Is chat_server.py running?")
        return

    # Keep the main thread alive so the background SocketIO thread can run
    print("\nClient connected. Type 'quit' to exit.")
    
    while sio.connected:
        try:
            # Simple text input loop
            user_input = input(f"{USERNAME} > ")
            if user_input.lower() == 'quit':
                break
            
            if user_input:
                # Send the message to the server
                sio.emit('client_message', {
                    'user': USERNAME,
                    'text': user_input
                })

        except EOFError:
            # Handles Ctrl+D/Ctrl+Z
            break
        except KeyboardInterrupt:
            # Handles Ctrl+C
            break
    
    sio.disconnect()
    print("Client gracefully shut down.")


if __name__ == '__main__':
    run_client()
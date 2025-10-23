import socket
import threading

HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5555
clients = []

class OnlineGame:
    def __init__(self):
        self.code = self.create_code()
        self.clients = []
        self.table = None

    def create_code(self):
        return '5555'

    def start_server(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((HOST, PORT))
        self.server.listen()
        print(f"[Online game started] Listening on {HOST}:{PORT}")
        threading.Thread(target=self.server_connections, daemon=True).start()

    def accept_connections(self):
        while True:
            conn, addr = self.server.accept()
            threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

    def handle_client(self, conn, addr):
        print(f"[CONNECTED] {addr}")
        self.clients.append(conn)
        try:
            while True:
                data = conn.recv(1024)
                if data:
                    self.apply_move(data, sender=conn)
        finally:
            print(f"[DISCONNECTED] {addr}")
            self.clients.remove(conn)
            conn.close()

    def apply_move(self, data, sender):
        if not self.valid_move():
            return False
        pass

    def valid_move(self):
        pass
    
    def broadcast(self, message, sender=None):
        for client in clients:
            if client != sender:
                client.sendall(message)


if __name__ == "__main__":
    # start_server()
    pass

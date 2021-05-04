import socket

ADDRESS = '127.0.1.1'
BASE_PORT = 60000


class Server:

    def __init__(self, pid) -> None:
        port = BASE_PORT + pid
        self.sock = self.create_socket(ADDRESS, port)

    def create_socket(self, addr, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((addr, port))
        return sock

    def handle_clients(self):
        pass

import socket

BASE_PORT = 60000
ADDRESS = '127.0.1.1'
BUFF_SIZE = 1024
RES_OK = 'OK'
RES_INVALID = 'INVALID'


class Client:

    def __init__(self, peers: list) -> None:
        self.peers = peers
        self.connections: list[socket.socket] = []

    def establish_conn2peers(self) -> None:
        for pid in self.peers:
            port = BASE_PORT + pid
            sock = self.create_socket(ADDRESS, port)
            self.connections.append(sock)
            print(f'[+] TCP connection established to peer {pid}.')
            status_code, status_text = self.authenticate(sock)
            if status_code == RES_OK:
                print(f'[+] Authenticated to peer {pid}')
            else:
                print(f'[-] Failed to authenticate to peer {pid}')
                print(f'[*] Response: {status_text}')

    def create_socket(self, addr, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(addr, port)

    def authenticate(self, sock: socket.socket):
        self.send_msg(sock, 'USER username\r\n')
        response = sock.recv(BUFF_SIZE)
        response = response.rstrip()
        status_code, status_text = response.split(" ")
        return status_code, status_text

    def flood(self, msg: str):
        for sock in self.connections:
            self.send_msg(sock, msg)

    def send_msg(self, sock: socket.socket, msg: str):
        sock.sendall(str.encode('ascii'))

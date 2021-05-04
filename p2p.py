from datetime import datetime
import sys
import socket
from _thread import *
import threading
from time import sleep

ADDRESS = '127.0.1.1'
BASE_PORT = 60000
BUFF_SIZE = 256
RES_OK = 'OK'
RES_INVALID = 'INVALID'
SLEEP_TIME = 5


class Peer:
    def __init__(self, addr: str, pid: int) -> None:
        self.addr = addr
        self.pid = pid
        self.peers = self.get_peers2_connect()
        self.connections: list[socket.socket] = []
        self.forwarded_msgs: dict[str] = {}

    def run(self):
        threading.Thread(target=self.server).start()
        threading.Thread(target=self.client).start()

    def server(self):
        sock = self.create_socket()
        address = (ADDRESS, BASE_PORT + self.pid)
        sock.bind(address)
        sock.listen(1)
        print(f'[SERVER {self.pid}] started...')

        while True:
            conn, addr = sock.accept()
            print(f'[SERVER {self.pid}] Connected to {addr}.')
            start_new_thread(self.client_handler, (conn, ))

    def client_handler(self, conn: socket.socket):
        while True:
            data: bytes = conn.recv(BUFF_SIZE)
            if data:
                msg: str = data.decode('ascii')
                command = msg.split(' ')[0]
                if command == 'FLOD':
                    self.forward(msg)
                elif command == 'EXIT':
                    pass

    def client(self):
        print(f'[CLIENT {self.pid}] is connecting to peers {self.peers}...')
        self.connect_to_peers()
        sleep_time = 60 - datetime.utcnow().second
        print(f'[{self.pid}] is waiting till minute ({sleep_time}s)...')
        sleep(sleep_time)
        self.flood()

    def connect_to_peers(self) -> None:
        p: list = self.peers[:]
        while len(p) > 0:
            for pid in p:
                sock = self.create_socket()
                try:
                    sock.connect((ADDRESS, BASE_PORT + pid))
                    self.connections.append(sock)
                    p.remove(pid)
                    print(
                        f'[CLIENT {self.pid}] established TCP connection to peer {pid}.')
                except Exception as e:
                    pass
            # status_code, status_text = self.authenticate(sock)
            # if status_code == RES_OK:
            #     print(f'[+] Authenticated to peer {pid}')
            # else:
            #     print(f'[-] Failed to authenticate to peer {pid}')
            #     print(f'[*] Response: {status_text}')

    def flood(self):
        for _ in range(3):
            for conn in self.connections:
                flood_time = datetime.now().strftime('%H:%M:%S')
                msg = f'FLOD {self.pid} {flood_time}'
                self.send_msg(msg, conn)
            sleep(SLEEP_TIME)

    def forward(self, msg):
        is_forwarded = self.forwarded_msgs.__contains__(msg)
        if not is_forwarded:
            print(
                f'[{self.pid}] Received -> {msg} ==> FORWARDING\nLIST ==> {self.forwarded_msgs}')
            for conn in self.connections:
                self.send_msg(msg, conn)
            self.forwarded_msgs[msg] = 1
        else:
            print(f'[{self.pid}] Received -> {msg} ==> NOT FORWARDING')
            self.forwarded_msgs[msg] += 1
            pass

    def authenticate(self, sock: socket.socket):
        self.send_msg(sock, 'USER username\r\n')
        response = sock.recv(BUFF_SIZE)
        response = response.rstrip()
        status_code, status_text = response.split(" ")
        return status_code, status_text

    def create_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock

    def send_msg(self, msg: str, sock: socket.socket):
        msg = msg.encode('ascii')
        sock.sendall(msg)

    def get_peers2_connect(self):
        peers = []
        with open('topology.txt', 'r') as f:
            # Number of peers
            n = f.readline().strip().replace(r'\r\n', '')
            for line in f.readlines():
                stripped_line = line.rstrip().replace(r'\r\n', '')
                src, dst = stripped_line.split('->')
                if int(src) == self.pid:
                    peers.append(int(dst))
        return peers


def parse_args(name="default", peer_id=1, addr="127.0.1.1"):
    return addr, int(peer_id)


def routine_handler(routine):
    print(routine)


if __name__ == '__main__':
    addr, pid = parse_args(*sys.argv)
    peer = Peer(ADDRESS, pid)
    peer.run()

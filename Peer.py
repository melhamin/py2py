import sys
import socket
from _thread import *
import threading

ADDRESS = '127.0.0.1'
BASE_PORT = 60000


def parse_args(name="default", addr="127.0.1.1", peer_id=1):
    return addr, int(peer_id)


def get_peers2_connect(id: int):
    peers = []
    with open('topology.txt', 'r') as f:
        # Number of peers
        n = f.readline().strip().replace(r'\r\n', '')
        for line in f.readlines():
            stripped_line = line.rstrip().replace(r'\r\n', '')
            src, dst = stripped_line.split('->')
            if int(src) == id:
                peers.append(int(dst))
    return peers


def client_routine(conn: socket.socket):
    while 1:
        data = conn.recv(1024)
        if data == 'q':
            conn.close()
            break
        send_data = f'Received data: {data}\nStatus code: 200'
        conn.sendall(send_data.encode())
    # conn.close()


def create_socket(addr, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((addr, port))
    return sock


# Parse command line arguments and toplogy
addr, peer_id = parse_args(*sys.argv)
# Peers that this peer should connect to
peers = get_peers2_connect(peer_id)

# Create a socket
sock = create_socket(ADDRESS, peer_id)
sock.listen(5)
print('[+] Server started...')

while True:
    conn, addr = sock.accept()
    print(f'[+] Connected to {addr}')
    start_new_thread(client_routine, (conn, ))

import socket
import sys
import threading
from _thread import *
from datetime import datetime
from time import sleep

ADDRESS = '127.0.1.1'
BASE_PORT = 60000
BUFF_SIZE = 512
RES_OK = 'OK'
RES_INVALID = 'INVALID'
SLEEP_TIME = 5
NUM_OF_MSGS = 7
USERNAME = 'bilkentstu'
PASS = 'cs421s2021'


class Peer:
    def __init__(self, addr: str, pid: int) -> None:
        self.addr = addr
        self.pid = pid
        self.peers = self.get_pids()
        self.connections: list[socket.socket] = []
        self.forwarded_msgs: dict[str] = {}
        self.lock = threading.Lock()

    def run(self):
        """ 
        Runs the server as the main thread and client in a new thread.
        """
        threading.Thread(target=self.client).start()
        self.server()

    def server(self):
        """ 
        Handles the server side of peer.\n
        Sever listens for incoming connection and creates
        a new thread for each client
        """
        sock = self.create_socket()
        address = (ADDRESS, BASE_PORT + self.pid)
        sock.bind(address)
        sock.listen(1)

        while True:
            conn, addr = sock.accept()
            threading.Thread(target=self.client_handler, args=(conn, )).start()

    def client_handler(self, conn: socket.socket):
        """ 
        Handles requests from the given connection.

        Parameters
        ----------
        conn: socket The TCP connection.
        """
        while True:
            data: bytes = conn.recv(BUFF_SIZE)
            if data:
                msg: str = data.decode('ascii').strip()
                msg_details = msg.split(' ')
                req_code = msg_details[0]
                if req_code == 'FLOD':
                    threading.Thread(target=self.forward, args=(msg, )).start()
                elif req_code == 'USER':
                    if msg_details[1] == USERNAME:
                        self.send_msg(f'{RES_OK} Success\r\n', conn)
                    else:
                        self.send_msg(
                            f'{RES_INVALID} Invalid username!\r\n', conn)
                elif req_code == 'PASS':
                    if msg_details[1] == PASS:
                        self.send_msg(f'{RES_OK} Success\r\n', conn)
                    else:
                        self.send_msg(
                            f'{RES_INVALID} Invalid password!\r\n', conn)

                elif req_code == 'EXIT':
                    conn.close()
                    break

    def client(self):
        """ 
        Handles the client side of this peer.
        Connects to other peers based on the toplogy.
        Client side floods the network every 5 seconds for 7 times.
        Closes connections after flooding is finished.
        """
        self.connect_to_peers()
        sleep_time = 60 - datetime.utcnow().second
        print(f'Waiting till next minute ({sleep_time}s)...')
        sleep(sleep_time)
        self.flood()
        self.shutdown()
        self.print_stats()

    def connect_to_peers(self) -> None:
        """
        Connects and authenticates to the peers with peer ids 
        extracted from the topology.
        No further action is taken in case of failure.
        After an attempt to connect and authenticate, the peer
        id is removed from the list of peers
        """

        while len(self.peers) > 0:
            for pid in self.peers:
                sock = self.create_socket()
                try:
                    sock.connect((ADDRESS, BASE_PORT + pid))
                    self.connections.append(sock)
                    print(
                        f'TCP connection established with peer {pid}.')
                    success, status_text = self.authenticate(sock)
                    if success:
                        print(f'Authenticated to peer {pid}')
                    else:
                        print(f'Failed to authenticate to peer {pid}')
                        print(f'Response: {status_text}')
                    self.peers.remove(pid)
                except Exception as e:
                    self.peers.remove(pid)

    def flood(self):
        """ 
        Sends the peer's id with timestamp to all
        of the connected peers after every 5 seconds
        """
        for _ in range(NUM_OF_MSGS):
            for conn in self.connections:
                flood_time = datetime.now().strftime('%H:%M:%S')
                msg = f'FLOD {self.pid} {flood_time}'
                self.send_msg(msg, conn)
                # self.lock.acquire(blocking=True)
                self.forwarded_msgs[msg] = 0
                # self.lock.release()
            sleep(SLEEP_TIME)

    def forward(self, msg: str):
        """ 
        Forwards the given message to all peers (if not already forwarded).
        If message is already forwarded, it increments its counter in the
        forwarded messages list.

        Parameters
        ----------
        msg: str -> The message to be forwarded.
        """
        self.lock.acquire(blocking=True)
        is_forwarded = self.forwarded_msgs.__contains__(msg)
        if not is_forwarded:
            print(f'Received -> {msg} [FORWARD]')
            for conn in self.connections:
                self.send_msg(msg, conn)
            # self.lock.acquire(blocking=True)
            self.forwarded_msgs[msg] = 1
            # self.lock.release()
        else:
            print(f'Received -> {msg} [DON\'T FORWARD]')
            # self.lock.acquire(blocking=True)
            self.forwarded_msgs[msg] += 1
            # self.lock.release()
        self.lock.release()

    def authenticate(self, sock: socket.socket):
        """ 
        Authenticates to the peer of the given connection.

        Parameters
        ----------
        sock: socket -> Peer connection.            

        Returns
        -------
        True, status_text: -> On success.
        False, status_text: -> On failure.                                                
        """
        self.send_msg(f'USER {USERNAME}\r\n', sock)
        response = sock.recv(BUFF_SIZE)
        response = response.decode().strip()
        index = response.index(' ')
        status_code = response[: index]
        status_text = response[index:]

        if status_code != RES_OK:
            return False, status_text

        self.send_msg(f'PASS {PASS}\r\n', sock)
        response = sock.recv(BUFF_SIZE)
        response = response.decode().strip()
        index = response.index(' ')
        status_code = response[: index]
        status_text = response[index:]

        if status_code != RES_OK:
            return False, status_text
        return True, status_text

    def shutdown(self):
        """ 
        Closes connection to all peers.
        """
        for conn in self.connections:
            msg = 'EXIT\r\n'
            self.send_msg(msg, conn)
            conn.close()

    def create_socket(self):
        """
        Creates a socket object.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock

    def send_msg(self, msg: str, sock: socket.socket):
        """ 
        Sends the given message through the given connection.

        Parameters
        ----------
        msg: str -> Message to be sent.
        sock: socket -> The connection.
        """
        msg = msg.encode('ascii')
        sock.sendall(msg)

    def get_pids(self):
        """ 
        Parses the peer ids from the toplogy that this peer should initiate a TCP connection with.

        Return
        ------
        peers: list -> Ids of peers.
        """
        peers = []
        with open('OverlayNetworkTopology.txt', 'r') as f:
            # Number of peers
            n = f.readline().strip().replace(r'\r\n', '')
            for line in f.readlines():
                stripped_line = line.rstrip().replace(r'\r\n', '')
                src, dst = stripped_line.split('->')
                if int(src) == self.pid:
                    peers.append(int(dst))
        return peers

    def print_stats(self):
        print('-' * 20 + f'PEER-{self.pid}' + '-' * 20)
        for msg, count in self.forwarded_msgs.items():
            message = msg.split(' ')
            # _, src_id, timestamp = msg.split(' ')
            print(f'{message[1]}\t\t{message[2]}\t\t{count}')


def parse_args(name="default", addr="127.0.1.1", peer_id=1):
    return addr, int(peer_id)


if __name__ == '__main__':
    addr, pid = parse_args(*sys.argv)
    peer = Peer(ADDRESS, pid)
    peer.run()

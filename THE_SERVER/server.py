import socket
import threading
from typing import Dict, List

from client import Client
from classes import CLIENTS, Communicator

HOST = '10.100.102.24'
PORT = 65432
RECVR: Client = None

class Server():

    def __init__(self) -> None:
        self.socket = socket.socket()
        self.num_of_threads = 0
        self.clients: List[Client] = []
        self.thread = threading.Thread(target=self.main_loop)
        try:
            self.socket.bind((HOST, PORT))
        except socket.error as e:
            print(str(e))
        print('Socket is listening..')
        self.socket.listen(5)

    def main_loop(self):
        pass

    def input_listener(self):

        global RECVR

        comm = Communicator()
        while True:
            inp = input().split(maxsplit=1)
            if inp[0] != "quit":
                if inp[0] == "client":
                    RECVR = CLIENTS[int(inp[1])]
                
                if RECVR is not None:
                    comm.pipe(RECVR, inp[0] + " " + inp[1])
                else:
                    print("Can't execute command as no client was chosen")
            else:
                self.socket.close()
                break

    def run(self):

        threading.Thread(target=self.input_listener).start()
        with self.socket:
            while True:
                clientconn, address = self.socket.accept()
                print('Connected to: ' + address[0] + ':' + str(address[1]))
                client = Client(self.num_of_threads, str(
                    clientconn.recv(2048), 'ascii'), clientconn)
                client.socket.sendall(bytes('Server recognizes you as %s %s' % (client.type, client.id), 'ascii'))
                if self.num_of_threads == 0:
                    RECVR = client
                threading.Thread(target=CLIENT_TYPES[client.type], args=(client,)).start()
                print("%s is connected & handled by thread %s" %
                    (client.type, client.id))
                CLIENTS.append(client)
                self.num_of_threads += 1

def mineSweeper(client: Client):

    global NUM_OF_THREADS

    comm = Communicator()
    with client.socket:
        while True:
            data = comm.listen(client)
            print(data)
            if not data:
                break

        del CLIENTS[client.id]
        NUM_OF_THREADS -= 1


def snake():
    pass

CLIENT_TYPES: Dict[str, callable] = {"minesweeper": mineSweeper,
                                     "snake": snake
                                     }




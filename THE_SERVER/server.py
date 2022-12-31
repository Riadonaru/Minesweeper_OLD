import socket
import threading
from typing import Dict, List

from classes import Communicator
from client import Client

HOST = '10.100.102.24'
PORT = 65432
RECVR: Client = None

class Server():

    def __init__(self) -> None:
        self.socket = socket.socket()
        try:
            self.socket.bind((HOST, PORT))
        except socket.error as e:
            print(str(e))
        self.client_num = 0
        self.clients: List[Client] = []
        self.thread = threading.Thread(target=self.run)
        print('Socket is listening..')
        self.socket.listen(5)

    # def input_listener(self):

    #     global RECVR

    #     comm = Communicator()
    #     while True:
    #         inp = input().split(maxsplit=1)
    #         if inp[0] != "quit":
    #             if inp[0] == "client":
    #                 RECVR = CLIENTS[int(inp[1])]
                
    #             if RECVR is not None:
    #                 comm.pipe(RECVR, inp[0] + " " + inp[1])
    #             else:
    #                 print("Can't execute command as no client was chosen")
    #         else:
    #             self.socket.close()
    #             break
    
    
    def mineSweeper(self):
        comm = Communicator()
        with self.socket:
            while True:
                data = comm.listen(self)
                print(data)
                if not data:
                    break

            del self.clients[self.id]
            self.client_num -= 1
            
    def snake(self):
        pass


    def run(self):

        # threading.Thread(target=self.input_listener).start()
        with self.socket:
            while True:
                clientconn, address = self.socket.accept()
                print('Connected to: ' + address[0] + ':' + str(address[1]))
                new_client = Client(self.client_num, str(
                    clientconn.recv(2048), 'ascii'), clientconn)
                new_client.socket.sendall(bytes('Server recognizes you as %s %i' % (new_client.type, new_client.id), 'ascii'))
                print("%s is connected & handled by thread %s" % (new_client.type, new_client.id))
                self.clients.append(new_client)
                self.client_num += 1

    types: Dict[str, callable] = {"minesweeper": mineSweeper,
                                        "snake": snake
                                }




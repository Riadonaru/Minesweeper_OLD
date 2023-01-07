import math
import numpy as np
import signal
import socket
import os
import threading
from typing import List

from client import Client
import globals
from message import Message

class Server():

    def __init__(self) -> None:
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        for i in range(globals.MAX_RETRIES):
            try:
                self.socket.bind((globals.HOST, globals.PORT))
                break
            except socket.error as e:
                if i >= globals.MAX_RETRIES - 1:
                    raise Exception(e)
        self.clients: List[Client] = []
        self.inThread = threading.Thread(target=self.usr_inpt)
        self.thread = threading.Thread(target=self.run)
        self.target_client_id = 0
        print('Listening for incoming connections...')
        self.socket.listen(globals.MAX_CONNECTIONS)

    def next_client_id(self):
        for i, client in enumerate(self.clients):
            if not client:
                del self.clients[i]
                return i
            
        return len(self.clients)

    def usr_inpt(self):
        while True:
            inpt = input()
            if inpt:
                splinpt = inpt.split(maxsplit=1)
                match splinpt[0]:
                    case "help":
                        with open(globals.PATH + "HELP.md") as f:
                            print(f.read())

                    case "switch":
                        try:
                            new_id = int(splinpt[1])
                            if new_id >= len(self.clients) or self.clients[new_id] == None:
                                print("switch: client id must be in %s" % [id for id in range(len(self.clients)) if self.clients[id] != None])
                            else:
                                self.target_client_id = int(splinpt[1])
                        except ValueError :
                            print("switch: client id must be a number!")

                    case "shutdown":
                        try:
                            if splinpt[1][:3] == "-a":
                                for client in self.clients:
                                    if client != None:
                                        msg = Message("shutdown", client.id, client.socket)
                                        msg.send()
                        except Exception:
                            pass
                        os.kill(os.getpid(), signal.SIGTERM)
                    case _:
                        if len(self.clients) > 0:
                            target_client = self.clients[self.target_client_id]
                            if target_client != None:
                                msg = Message(inpt, self.target_client_id, target_client.socket)
                                msg.send()
                            else:
                                print("Client %i is no longer connected!" % self.target_client_id)
                        else:
                            print("No client is connected...")

    def output(self, client: Client):
        get = False
        while True:
            msg = Message.decipher(client.socket.recv(globals.MAX_MSG_LEN))
            if msg == None:
                self.clients[client.id] = None
                print("Client %i disconnected" % client.id)
                break
            if get:
                get = False
                num_arr = msg.get_content().split()
                sqr_edge = int(math.sqrt(len(num_arr)))
                data = np.reshape(num_arr, (sqr_edge, sqr_edge))
                for list in data:
                    for num in list:
                        num = str(num)
                        if len(num) == 1:
                            num = " " + num
                        print(num, end=" ")
                    print()
            else:
                msg.print_content()

            if msg.get_content().split(maxsplit=1)[0] == "get":
                get = True

    def run(self):
        if not self.inThread.is_alive():
            self.inThread.start()

        with self.socket:
            while True:
                try:
                    socket, address = self.socket.accept()
                except:
                    print("\nStopped listening to incoming connections")
                    break
                print('Connected to: ' + address[0] + ':' + str(address[1]))
                next_id = self.next_client_id()
                self.clients.insert(next_id, Client(next_id, socket, self.output))

import signal
import socket
import os
import threading
from typing import List

from client import Client
import globals
from message import Message
import time

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
        self.client_num = 0
        self.clients: List[Client] = []
        self.inThread = threading.Thread(target=self.usr_inpt)
        self.thread = threading.Thread(target=self.run)
        self.target_client_id = 0
        print('Listening for incoming connections...')
        self.socket.listen(globals.MAX_CONNECTIONS)


    def usr_inpt(self):
        while True:
            inpt = input()
            splinpt = inpt.split(maxsplit=1)
            match splinpt[0]:
                case "switch":
                    self.target_client_id = int(splinpt[1])
                case "shutdown":
                    os.kill(os.getpid(), signal.SIGTERM)
                case _:
                    msg = Message(inpt, self.target_client_id, self.clients[self.target_client_id].socket)
                    msg.send()

    def run(self):
        if not self.inThread.is_alive():
            self.inThread.start()

        with self.socket:
            while True:
                try:
                    socket, address = self.socket.accept()
                except:
                    print("Socket stopped listening to incoming connections")
                    break
                print('Connected to: ' + address[0] + ':' + str(address[1]))
                new_client = Client(self.client_num, socket)
                self.clients.append(new_client)
                self.client_num += 1

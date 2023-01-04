import socket
import threading
import time
from message import Message
import globals


class Client():
    
    def __init__(self, id: int, socket: socket.socket) -> None:
        self.id = id
        self.type = None # TODO Snake/Minesweeper/PacMan, etc...
        self.socket = socket
        message = Message("Connection successful!", self.id, self.socket)
        message.send()
        self.outThread = threading.Thread(target=self.output)
        self.outThread.start()
        self.nn = None # TODO make a way for each client to access the population
    
    def ping(self):
        i = 0
        while True:
            msg = Message("\nPinging... %i" % i, self.id, self.socket)
            msg.send()
            i += 1
            time.sleep(1)


    def output(self):
        while True:
            msg = Message.decipher(self.socket.recv(globals.MAX_MSG_LEN))
            if msg == None:
                print("Client %i disconnected" % self.id)
                break
            msg.print_content()

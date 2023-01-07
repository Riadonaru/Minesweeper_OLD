import socket
import threading
import time
from message import Message
import globals


class Client():
    
    def __init__(self, id: int, socket: socket.socket, action: callable) -> None:
        self.id = id
        self.type = None # TODO Snake/Minesweeper/PacMan, etc...
        self.socket = socket
        self.thread = threading.Thread(target=action, args=(self,))
        self.thread.start()
        message = Message("Connection successful!", self.id, self.socket)
        message.send()
        self.nn = None # TODO make a way for each client to access the population
    
    def ping(self):
        i = 0
        while True:
            msg = Message("\nPinging... %i" % i, self.id, self.socket)
            msg.send()
            i += 1
            time.sleep(1)


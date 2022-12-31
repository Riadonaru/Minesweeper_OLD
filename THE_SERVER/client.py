import socket
import threading
from server import 


class Client():
    
    def __init__(self, id: int, type: str, socket: socket.socket) -> None:
        self.id = id
        self.type = type # TODO Snake/Minesweeper/PacMan, etc...
        self.socket = socket
        self.thread = threading.Thread(target=Server.types[type](self))
        self.thread.run()
        self.nn = None # TODO make a way for each client to access the population
    

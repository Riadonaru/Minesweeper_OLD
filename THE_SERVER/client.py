import socket
import threading

class Client():
    
    def __init__(self, id: int, socket: socket.socket) -> None:
        self.id = id
        self.type = None # TODO Snake/Minesweeper/PacMan, etc...
        self.socket = socket
        self.thread = threading.Thread(target=self.main_loop)
        self.nn = None # TODO make a way for each client to access the population
    
    def main_loop(self):
        pass
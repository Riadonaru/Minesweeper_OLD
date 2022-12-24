import socket
import threading
from typing import List
from globals import SETTINGS, HOST, PORT, PLAYING
from game import Game
import time

class Client():

    def __init__(self) -> None:
        self.game = Game()
        self.inpt_src = SETTINGS["input_source"]
        self.socket: socket.socket = None
        self.id: int = None
        self.clientThread: threading.Thread = None
        self.timerThread = threading.Thread(target=self.timer)
        if SETTINGS["allow_command_input"]:
            self.clientThread = threading.Thread(target=self.client)

    def timer(self):
        while self.game.running:
            while self.game.grid.contents_created and self.game.grid.state == PLAYING:
                self.game.timer_running.wait()
                self.game.elapsed_time += 1
                time.sleep(1)

    def retry_connection(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((HOST, PORT))
            self.socket.sendall(b'minesweeper')
            data = str(self.socket.recv(2048), "ascii")
            print(data)
            self.id = int(data.split()[-1])
        except:
            print("Error trying to connect to the server")
            self.socket.close()

    def process_request(self, data: List[str]):

        match data[0]:

            case "say":
                print(data[1])
                if self.inpt_src == "server":
                    self.socket.sendall(b'aquired by client')

            case"client":
                if int(data[1]) == self.id:
                    self.socket.sendall(bytes('Successfully Connected to Client %s' % (self.id), 'ascii'))

            case "reveal":
                data = data[1].split()
                self.game.reveal(int(data[0]), int(data[1]))

            case "setting":
                data = data[1].split()
                match str(type(self.settings[data[0]])):
                    
                    case "<class 'bool'>":
                        if data[1] == "True":
                            SETTINGS[data[0]] = True
                        elif data[1] == "False":
                            SETTINGS[data[0]] = False
                        else:
                            self.socket.sendall(bytes(data[1] + " is not a valid entry!", 'ascii'))
                    
                    case "<class 'int'>":
                        SETTINGS[data[0]] = int(data[1])

                    case "<class 'str'>":
                        SETTINGS[data[0]] = str(data[1])
                
                self.game.set_settings()

            case "flag":
                data = data[1].split()
                self.game.flag(int(data[0]), int(data[1]))

            case "reset":
                self.game.reset()

            case _:
                print(data[0] + ": Command not found")

    def client(self):
        
        try:
            while self.game.running:
                self.inpt_src = SETTINGS["input_source"]

                if self.inpt_src == "client":
                    data = input()
                elif self.inpt_src == "server":
                    if self.socket is None or self.id is None:
                        self.retry_connection()
                    data = str(self.socket.recv(2048), "ascii")
                
                data = data.split(maxsplit=1)

                if not data:
                    break
                self.process_request(data)
        except Exception as e:
            print(e)
        finally:
            if self.socket is not None:
                self.socket.close()

    def run(self):
        self.game.running = True
        if self.clientThread is not None and not self.clientThread.is_alive():
            if SETTINGS["allow_command_input"]:
                self.clientThread.start()

        if not self.timerThread.is_alive():
            self.timerThread.start()
            self.game.timer_running.set()

        self.game.play()
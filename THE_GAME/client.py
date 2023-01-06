import os
import signal
import socket
import threading
from typing import List
from globals import MAX_RETRIES, PATH, SETTINGS, HOST, PORT, PLAYING, MAX_MSG_LEN
from game import Game
import time
from message import Message
from playsound import playsound

class Client():

    def __init__(self) -> None:
        self.game = Game()
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


    def process_request(self, data: List[str]):

        res = None
        match data[0]:
            case "say":
                print(data[1])
                
            case"client":
                res = "Hello from client %i" % self.id

            case "sound":
                playsound(PATH + "game-over.mp3")

            case "get":
                res = ""
                vars = data[1].split()
                for y in range(-2, 3):
                    for x in range(-2, 3):
                        res += " %i" % self.game.grid.contents[int(vars[0]) + y][int(vars[1]) + x].data()

            case "reveal":
                vars = data[1].split()
                self.game.reveal(int(vars[0]), int(vars[1]))

            case "flag":
                vars = data[1].split()
                self.game.flag(int(vars[0]), int(vars[1]))

            case "reset":
                self.game.reset()
            
            case "shutdown":
                os.kill(os.getpid(), signal.SIGTERM)

            case _:
                res = data[0] + ": Command not found"
                print(res)

        msg = Message(data[0], self.id, self.socket)
        msg.send()
        if res != None:
            msg = Message(res, self.id, self.socket)
            msg.send()

    def connect(self):
        i = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while self.socket is None or self.id is None:
            try:
                print("trying to connect to the server...")
                self.socket.connect((HOST, PORT))
                msg = Message.decipher(self.socket.recv(MAX_MSG_LEN))
                data = msg.get_content()
                self.id = int(msg.id)
                print(data, "Id: %i" % self.id)
                return True
            except ConnectionRefusedError:
                i += 1
                print("Try %i Failed" % i)
                if i >= MAX_RETRIES:
                    print("Couldn't connect to the server")
                    return False
                time.sleep(i)

    def client(self):
        
        if self.connect():
            with self.socket:
                while self.game.running:
                    msg = Message.decipher(self.socket.recv(MAX_MSG_LEN))
                    if msg == None:
                        print("Server died... :(")
                        self.socket = None
                        self.id = None
                        if not self.connect():
                            break # TODO FIX
                        else:
                            continue

                    data = msg.get_content().split(maxsplit=1)
                    self.process_request(data)


    def run(self):
        self.game.running = True
        if self.clientThread is not None and not self.clientThread.is_alive():
            if SETTINGS["allow_command_input"]:
                self.clientThread.start()

        if not self.timerThread.is_alive():
            self.timerThread.start()
            self.game.timer_running.set()

        self.game.play()
        self.socket.close()
        os.kill(os.getpid(), signal.SIGTERM)

        
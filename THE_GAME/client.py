import os
import signal
import socket
import threading
from typing import List
from globals import MAX_RETRIES, MINE, PATH, SETTINGS, HOST, PORT, PLAYING, MAX_MSG_LEN
from game import Game
import time
from message import Message
from playsound import playsound

class Client():

    def __init__(self) -> None:
        self.game = Game()
        self.id: int = None
        self.client_thread: threading.Thread = None
        self.timer_thread = threading.Thread(target=self.timer)
        if SETTINGS["allow_command_input"]:
            self.client_thread = threading.Thread(target=self.listen)

    def timer(self):
        while self.game.running:
            while self.game.grid.contents_created and self.game.grid.state == PLAYING:
                self.game.timer_running.wait()
                self.game.elapsed_time += 1
                time.sleep(1)


    def process_request(self, msg: Message):

        res = None
        data = msg.get_content().split(maxsplit=1)
        match data[0]:
            case "say":
                print("server:", data[1])
                
            case"client":
                res = "Hello from client %i" % self.id

            case "sound":
                playsound(PATH + "game-over.mp3")

            case "get":
                res = ""
                args = data[1].split()
                for y in range(-2, 3):
                    for x in range(-2, 3):
                        new_x = int(args[0]) + x
                        new_y = int(args[1]) + y
                        if 0 <= new_x < SETTINGS["width"] and 0 <= new_y < SETTINGS["height"]:
                            res += " %i" % self.game.grid.contents[new_y][new_x].data()
                        else:
                            res += " -4"

            case "reveal":
                args = data[1].split()
                mine_loc = self.game.reveal(int(args[0]), int(args[1]))
                if mine_loc:
                    res = "mine encountered at %s" % str(mine_loc)

            case "flag":
                args = data[1].split()
                self.game.flag(int(args[0]), int(args[1]))

            case "reset":
                self.game.reset()
            
            case "shutdown":
                print("server: shutdown requested")
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

    def listen(self):
        
        if self.connect():
            with self.socket:
                while self.game.running:
                    msg = Message.decipher(self.socket.recv(MAX_MSG_LEN))
                    if msg == None:
                        print("Server died... :(")
                        self.socket = None
                        self.id = None
                        if not self.connect():
                            break
                        else:
                            continue

                    self.process_request(msg)


    def run(self):
        self.game.running = True
        if self.client_thread is not None and not self.client_thread.is_alive():
            if SETTINGS["allow_command_input"]:
                self.client_thread.start()

        if not self.timer_thread.is_alive():
            self.timer_thread.start()
            self.game.timer_running.set()

        self.game.play()
        self.socket.close()
        os.kill(os.getpid(), signal.SIGTERM)

        
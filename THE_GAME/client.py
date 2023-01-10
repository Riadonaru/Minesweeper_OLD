import os
import signal
import socket
import threading
import time

from game import Game
from globals import HOST, MAX_MSG_LEN, MAX_RETRIES, PATH, PORT, SETTINGS
from message import Message
from playsound import playsound


class Client(Game):

    def __init__(self) -> None:
        self.id: int = None
        self.thread: threading.Thread = None
        self.input_thread: threading.Thread = None
        if SETTINGS["allow_command_input"]:
            self.thread = threading.Thread(target=self.listen)
            self.input_thread = threading.Thread(target=self.usr_input)
        super().__init__()

    def usr_input(self):
        inp = Message(input(), self.id)
        self.process_request(msg=inp)
    
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
                            res += " %i" % self.grid.contents[new_y][new_x].data()
                        else:
                            res += " -4"

            case "reveal":
                args = data[1].split()
                mine_loc = self.reveal(int(args[0]), int(args[1]))
                if mine_loc:
                    res = "mine encountered at %s" % str(mine_loc)

            case "flag":
                args = data[1].split()
                self.flag(int(args[0]), int(args[1]))

            case "setting":
                vars = data[1].split()
                setting = vars[0]
                if setting in SETTINGS.keys():
                    val = vars[1]
                    val = type(SETTINGS[setting])(val)
                    SETTINGS[setting] = val
                    self.game.set_settings()
                else:
                    print("%s is not a valid setting! Valid settings: %s" % (vars[0], SETTINGS.keys()))
            case "reset":
                self.reset()
            
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
        if all(key in SETTINGS["server_data"] for key in ("host", "port")):
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
                while self.running:
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
        if SETTINGS["allow_command_input"]:
            if self.thread is not None and not self.thread.is_alive():
                self.thread.start()
                    
            if self.input_thread is not None and not self.input_thread.is_alive():
                self.input_thread.start()
        
        super().run()
        self.socket.close()
        os.kill(os.getpid(), signal.SIGTERM)
        
    

        
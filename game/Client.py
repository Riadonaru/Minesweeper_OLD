import json
import socket
from turtle import st

import Minesweeper

HOST = "10.100.102.24"  # The server's hostname or IP address
PORT = 65432  # The port used by the server


def client(game: Minesweeper.Game):

    global INPUT_SOURCE, SETTINGS_SPR
    
    s: socket.socket = None
    myId: int = None
    try:
        while game.runing:
            INPUT_SOURCE = game.settings["input_source"]

            if INPUT_SOURCE == "client":
                data = input()
            elif INPUT_SOURCE == "server":
                if s is None or myId is None:
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.connect((HOST, PORT))
                        s.sendall(b'minesweeper')
                        data = str(s.recv(2048), "ascii")
                        print(data)
                        myId = int(data.split()[-1])
                    except:
                        print("Error trying to connect to the server")
                        s.close()
                data = str(s.recv(2048), "ascii")
            
            data = data.split(maxsplit=1)

            if not data:
                break
            
            match data[0]:

                case "say":
                    print(data[1])
                    if INPUT_SOURCE == "server":
                        s.sendall(b'aquired by client')

                case"client":
                    if int(data[1]) == myId:
                        s.sendall(bytes('Successfully Connected to Client %s' % (myId), 'ascii'))

                case "reveal":
                    data = data[1].split()
                    game.reveal(int(data[0]), int(data[1]))

                case "setting":
                    data = data[1].split()
                    match str(type(game.settings[data[0]])):
                        
                        case "<class 'bool'>":
                            if data[1] == "True":
                                game.settings[data[0]] = True
                            elif data[1] == "False":
                                game.settings[data[0]] = False
                            else:
                                s.sendall(bytes(data[1] + " is not a valid entry!", 'ascii'))
                        
                        case "<class 'int'>":
                            game.settings[data[0]] = int(data[1])

                        case "<class 'str'>":
                            game.settings[data[0]] = str(data[1])
                    
                    game.setSettings()

                case "flag":
                    data = data[1].split()
                    game.flag(int(data[0]), int(data[1]))

                case "reset":
                    game.restart()

                case "secret":
                    SETTINGS_SPR = 12
                    game.settings_button.content = SETTINGS_SPR

                case _:
                    print(data[0] + ": Command not found")

    except Exception as e:
        print(e)
    finally:
        if s is not None:
            s.close()

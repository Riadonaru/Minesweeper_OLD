from os import stat
import socket
import threading
from typing import Any, List

class Client():

    _acceptedClientTypes = {"bot", "game"}

    def __init__(self, id: int, type: str, socket: socket.socket) -> None:
        self.id = id
        self.type = type  # Bot, Game, etc.
        self.socket = socket
        self.__recvrId = -1


    @property
    def recvrId(self):
        return self.__recvrId


    @recvrId.setter
    def recvrId(self, __value: int):
        self.__recvrId = __value


    @property
    def type(self):
        return self.__type


    @type.setter
    def type(self, __value):
        if __value in Client._acceptedClientTypes:
            self.__type = __value
        else:
            raise Exception("Client type cannot be " + __value + "!")

    def forward(self, message: List[str]):
        pass



class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

# Python3


class Communicator(metaclass=Singleton):

    _botValidMessages = {"game", "reveal", "flag", "reset"}
    _gameValidMessages = {"win", "lose", "error", "success"}

    @staticmethod
    def pipe(fromClient: Client, message: str):
        CLIENT_TYPES[fromClient.type](fromClient, message)

    @staticmethod
    def game(fromClient: Client, message: str):
        CLIENTS[fromClient.recvrId].socket.sendall(bytes(message, 'ascii'))  

    @staticmethod
    def bot(fromClient: Client, message: str):
        CLIENTS[fromClient.recvrId].socket.sendall(bytes(message, 'ascii'))


                    
CLIENTS: List[Client] = []
CLIENT_TYPES = {"bot": Communicator.bot, 
                "game": Communicator.game
                }
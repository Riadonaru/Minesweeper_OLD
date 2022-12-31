from client import Client

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
        CLIENTS[fromClient.id].socket.sendall(bytes(message, 'ascii'))

    @staticmethod
    def listen(client: Client):
        return str(client.socket.recv(2048), 'ascii')
                    
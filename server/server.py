import socket
import threading
from typing import Dict, List

from classes import CLIENTS, Communicator, Client

HOST = '127.0.0.1'
PORT = 65432
STOP = False


ServerSideSocket = socket.socket()
try:
    ServerSideSocket.bind((HOST, PORT))
except socket.error as e:
    print(str(e))
print('Socket is listening..')
ServerSideSocket.listen(5)


def inputListener():
    global STOP

    while not STOP:
        if input() == "exit":
            STOP = True


def botHandler(client: Client):
    global STOP

    comm = Communicator()
    with client.socket:
        while not STOP:
            if client.recvrId == -1:
                try:
                    client.socket.sendall(b'Input a gameId to connect to')
                    client.recvrId = int(client.socket.recv(2048))
                    print("init %s" % client.id)
                    comm.pipe(client, "init %s" % client.id)
                except:
                    client.socket.sendall(b'GameId must be an integer!')
            data = str(client.socket.recv(2048), 'ascii')
            if data == "quit":
                STOP = True
            if not data:
                break
            # comm.pipe(client, data)
            print(data)


def gameHandler(client: Client):
    global STOP

    comm = Communicator()
    with client.socket:
        while not STOP:
            data = str(client.socket.recv(2048), 'ascii')
            bata = data.split()
            if client.recvrId == -1 and bata[0] == "connected":
                client.recvrId = int(bata[1])
                print(data)

            if data == "quit":
                STOP = True

            if not data:
                break
            comm.pipe(client, data)

CLIENT_TYPES: Dict[str, callable] = {"bot": botHandler,
                                     "game": gameHandler
                                     }

num_of_threads = 0
with ServerSideSocket:
    while not STOP:
        clientconn, address = ServerSideSocket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        client = Client(num_of_threads, str(
            clientconn.recv(2048), 'ascii'), clientconn)
        client.socket.sendall(bytes('Server recognizes you as %s' % client.type, 'ascii'))
        threading.Thread(target=CLIENT_TYPES[client.type], args=(client,)).start()
        print("%s is connected & handled by thread %s" %
              (client.type, client.id))
        CLIENTS.append(client)
        print('Thread Number:', num_of_threads)
        num_of_threads += 1



from concurrent.futures import thread
import socket
import threading
from typing import Dict, List
from xmlrpc.client import Server

from classes import CLIENTS, Communicator, Client

HOST = '127.0.0.1'
PORT = 65432
RECVR: Client = None

ServerSideSocket = socket.socket()
try:
    ServerSideSocket.bind((HOST, PORT))
except socket.error as e:
    print(str(e))
print('Socket is listening..')
ServerSideSocket.listen(5)


def inputListener():

    global RECVR, ServerSideSocket

    comm = Communicator()
    while True:
        inp = input()
        if inp != "quit":

            if inp.startswith("client"):
                inp = inp.split()
                RECVR = CLIENTS[int(inp[1])]
                print("Now communicating with client", inp[1])
            else:
                comm.pipe(RECVR, inp)

        else:
            ServerSideSocket.close()
            break


def mineSweeper(client: Client):

    with client.socket:
        while True:
            data = str(client.socket.recv(2048), 'ascii')
            print(data)
            if not data:
                break


def snake():
    pass

CLIENT_TYPES: Dict[str, callable] = {"minesweeper": mineSweeper,
                                     "snake": snake
                                     }

num_of_threads = 0
threading.Thread(target=inputListener).start()
with ServerSideSocket:
    while True:
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



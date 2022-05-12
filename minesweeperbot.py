import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    inp = input()
    while inp != "exit":
        s.sendall(bytes(inp, "ascii"))
        data = str(s.recv(1024), "ascii")
        print(data)
        inp = input()
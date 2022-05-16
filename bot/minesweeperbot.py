import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'bot')
    print(str(s.recv(2048), 'ascii'))
    inp = ""
    while inp != "exit":
        try:
            data = str(s.recv(2048), 'ascii')
            if not data:
                break

            print(data)
            inp = input()
            s.sendall(bytes(inp, "ascii"))
        except Exception as e:
            print(e)
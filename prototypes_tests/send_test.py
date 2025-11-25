import socket
s = socket.socket()
s.connect(("127.0.0.1", 5002))
s.sendall(b"hello via router")
s.close()
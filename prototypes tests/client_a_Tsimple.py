import socket

HOST = "127.0.0.1"
PORT = 5001

s = socket.socket()
s.connect((HOST, PORT))
s.sendall(b"Bonjour du client !")
s.close()
print("Connexion au serveur fermée")
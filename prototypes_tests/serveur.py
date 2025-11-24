import socket
import threading

HOST = "127.0.0.1"
PORT = 5001

def handle_client(conn):
    data = conn.recv(4096).decode()
    print("Reçu :", data)
    conn.close()

s = socket.socket()
s.bind((HOST, PORT))
s.listen()

print(f"Serveur en écoute sur {PORT}")

while True:
    conn, addr = s.accept()
    threading.Thread(target=handle_client, args=(conn,)).start()

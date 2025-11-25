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
try:
    while True:
        try:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn,)).start()
        except socket.timeout:
            # on revient dans la boucle, ce qui permet de capter Ctrl+C
            continue
except KeyboardInterrupt:
    print("\n[CLIENT B] Arrêt demandé par l'utilisateur.")
finally:
    s.close()
    print("[CLIENT B] Socket fermé.")

while True:
    conn, addr = s.accept()
    threading.Thread(target=handle_client, args=(conn,)).start()

import socket
import threading

ROUTER_PORT = 5002
NEXT_HOP = ("127.0.0.1", 5003)  # routeur suivant ou Client B


def handle_client(conn):
    data = conn.recv(4096)
    print("Routeur a reçu:", data)

    # Transmet directement au prochain hop
    forward = socket.socket()
    forward.connect(NEXT_HOP)
    forward.sendall(data)
    forward.close()

    conn.close()


s = socket.socket()
s.bind(("127.0.0.1", ROUTER_PORT))
s.listen()

print(f"Routeur sur {ROUTER_PORT}")

while True:
    conn, addr = s.accept()
    threading.Thread(target=handle_client, args=(conn,)).start()

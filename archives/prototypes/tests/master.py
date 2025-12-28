# Master minimal :
#  - reçoit les clés publiques des routeurs
#  - fournit aux clients la liste des routeurs et leurs clés
# -------------------------------------------------------------------

import socket
import threading
from archives.prototypes.tests.utils import serialize, deserialize

ROUTERS = []     # liste de dict {addr, pubkey}

MASTER_PORT = 5000


def handle_client(conn, addr):
    data = conn.recv(4096)
    if not data:
        conn.close()
        return

    msg = deserialize(data)

    if msg["type"] == "register_router":
        ROUTERS.append({
            "addr": msg["addr"],
            "pubkey": msg["pubkey"]
        })
        print(f"[MASTER] Routeur enregistré : {msg['addr']}")

        conn.sendall(serialize({"status": "ok"}))

    elif msg["type"] == "request_keys":
        conn.sendall(serialize({"routers": ROUTERS}))

    conn.close()


def start_master():
    s = socket.socket()
    s.bind(("0.0.0.0", MASTER_PORT))
    s.listen()

    print(f"[MASTER] Écoute sur port {MASTER_PORT}")

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()


if __name__ == "__main__":
    start_master()

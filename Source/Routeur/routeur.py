# Routeur :
#  - génère sa paire de clés
#  - s’enregistre auprès du Master
#  - écoute les messages
#  - déchiffre une couche
#  - forward vers "dest"
# -------------------------------------------------------------------

import socket
import threading
import argparse
from utils import serialize, deserialize, parse_addr
import crypto

def register_with_master(master_addr, my_addr, pubkey):
    host, port = parse_addr(master_addr)
    s = socket.socket()
    s.connect((host, port))
    msg = {
        "type": "register_router",
        "addr": my_addr,
        "pubkey": pubkey
    }
    s.sendall(serialize(msg))
    s.close()
    print(f"[ROUTEUR] Enregistré auprès du Master.")


def forward(payload_bytes, dest_addr):
    host, port = parse_addr(dest_addr)
    s = socket.socket()
    s.connect((host, port))
    s.sendall(payload_bytes)
    s.close()


def handle_connection(conn, privkey):
    data = conn.recv(65536)
    if not data:
        conn.close()
        return

    # Déchiffrement d’une couche
    inner_json_bytes = crypto.decrypt_with_priv(privkey, data)
    inner = deserialize(inner_json_bytes)

    print(f"[ROUTEUR] Reçu couche déchiffrée -> dest={inner['dest']}")

    # Forward vers prochain hop
    forward(inner["payload"].encode("utf-8") if isinstance(inner["payload"], str) else inner["payload"],
            inner["dest"])

    conn.close()


def start_router(port, master_addr):
    pub, priv = crypto.generate_keypair()
    my_addr = f"127.0.0.1:{port}"

    # enregistrement master
    register_with_master(master_addr, my_addr, pub)

    # serveur
    s = socket.socket()
    s.bind(("0.0.0.0", port))
    s.listen()

    print(f"[ROUTEUR] Écoute sur {port}")

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_connection, args=(conn, priv)).start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--master", type=str, required=True)
    args = parser.parse_args()

    start_router(args.port, args.master)

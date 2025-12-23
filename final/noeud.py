import socket
import threading
import argparse
from rsa import (generate_keypair,
                 encrypt, serialize, # client
                 decrypt, deserialize) # routeur

#MASTER_ADDR = ("127.0.0.1", 4000)

CLIENT_B_IP = "127.0.0.1"
CLIENT_B_PORT = 6000


# routeur

def handle_packet(data, privkey):
    blocks = deserialize(data)
    plain = decrypt(privkey, blocks)

    dest, payload = plain.split(b"|", 1)
    ip, port = dest.decode().split(":")

    return ip, int(port), payload

def start_router(port):
    pub, priv = generate_keypair()
    print(f"[ROUTER {port}] Clé publique = {pub}")

    s = socket.socket()
    s.bind(("127.0.0.1", port))
    s.listen()
    print(f"[ROUTER {port}] Écoute")

    def handle(conn):
        data = conn.recv(4096)
        if not data:
            conn.close()
            return

        next_ip, next_port, payload = handle_packet(data, priv)

        forward = socket.socket()
        forward.connect((next_ip, next_port))
        forward.sendall(payload)
        forward.close()


        conn.close()

    while True:
        conn, _ = s.accept()
        threading.Thread(target=handle, args=(conn,), daemon=True).start()



# client A / construction oignon
def build_oignon(message: bytes, circuit):
    # Couche interne à destination du Client B
    payload = f"{CLIENT_B_IP}:{CLIENT_B_PORT}|".encode() + message

    # chiffrement en couches de l'intérieur vers l'extérieur
    for ip, port, pubkey in reversed(circuit):
        payload = serialize(encrypt(pubkey, payload))
        # La destination de la couche suivante est le routeur courant
        payload = f"{ip}:{port}|".encode() + payload

    return payload

def start_client_a(message: bytes):
    # CIRCUIT CODÉ EN DUR (MVP)
    # À remplacer plus tard par le master

    circuit = [
        ("127.0.0.1", 5002, (3233, 17)),  # Routeur 1 (clé publique)
        ("127.0.0.1", 5003, (2773, 17)),  # Routeur 2
    ]

    oignon = build_oignon(message, circuit)

    first_ip, first_port, _ = circuit[0]
    s = socket.socket()
    sock.connect(first_ip, first_port)
    sock.sendall(oignon)
    sock.close()

    print("[CLIENT] Message envoyé")

# client B / récépteur final
def start_client_b(port):
    s = socket.socket()
    s.bind("127.0.0.1", port)
    s.listen()
    print("[CLIENT B] Écoute")

    def handle(conn):
        data = conn.recv(4096)
        if data:
            print("[CLIENT B] Message reçu :", data)
        conn.close()

    while True:
        conn, _ = s.accept()
        threading.Thread(target=handle, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", choices=["router", "clienta", "clientb"], required=True)
    parser.add_argument("--port", type=int)
    parser.add_argument("--msg")
    args = parser.parse_args()

    if args.role == "router":
        start_router(args.port)

    if args.role == "clienta":
        start_client_a(args.msg.encode())

    if args.role == "clientb":
        start_client_b(args.port)


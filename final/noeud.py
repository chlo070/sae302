import socket
import threading
import argparse
import random
from rsa import (generate_keypair,
                 encrypt, serialize, # client
                 decrypt, deserialize) # routeur

#MASTER_ADDR = ("127.0.0.1", 4000)

CLIENT_B_IP = "127.0.0.1"
CLIENT_B_PORT = 6000

# routeur
def start_router(port):
    pub, priv = generate_keypair()
    print(f"[ROUTEUR {port}] Clé publique = {pub}")

    # socket REGISTER au master
    s = socket.socket()
    s.connect(("127.0.0.1", 4000))
    msg = f"REGISTER 127.0.0.1 {port} {pub[0]} {pub[1]}"
    s.sendall(msg.encode())
    s.close()

    # socket d'écoute
    server = socket.socket()
    server.bind(("127.0.0.1", port))
    server.listen()

    def handle(conn):
        data = conn.recv(4096)
        if not data:
            conn.close()
            return

        print(f"[ROUTEUR] Reçu: {data[:50]}...")

        try:
            # étape 1 : déchiffrement du payload uniquement/d'une couche
            blocks = deserialize(data)
            plain = decrypt(priv, blocks)
            print(f"[ROUTEUR] Plain: {plain[:50]}...")
            # étape 2 : extraction destination + payload
            dest, payload = plain.split(b"|", 1)
            ip, port_str = dest.decode().split(":")
            port = int(port_str)
            print(f"[ROUTEUR] Forward à {ip}:{port}, payload: {payload[:50]}...")
            # étape 3 : forward
            forward = socket.socket()
            forward.connect((ip, port))
            forward.sendall(payload)    # jonglage entre plain et payload
            forward.close()
            print(f"[ROUTEUR] Forward réussi à {ip}:{port}")
        except Exception as e:
            print(f"[ROUTEUR] Erreur: {e}")
        conn.close()

    while True:
        conn, _ = server.accept()
        threading.Thread(target=handle, args=(conn,), daemon=True).start()



# client A / construction oignon
def build_oignon(message: bytes, circuit):
    # Couche interne à destination du Client B
    # payload = message
    payload = f"{CLIENT_B_IP}:{CLIENT_B_PORT}|".encode() + message

    # chiffrement en couches de l'intérieur vers l'extérieur
    for ip, port, pubkey in reversed(circuit):
        # La destination de la couche suivante (le routeur courant)
        layer = f"{ip}:{port}|".encode() + payload
        payload = serialize(encrypt(pubkey, layer))

    return payload

def start_client_a(message: bytes):
    s = socket.socket()
    s.connect(("127.0.0.1", 4000))
    s.sendall(b"GET_CIRCUIT")

    data = b""
    while True:
        chunk = s.recv(4096)
        if not chunk:
            break
        data += chunk
    s.close()

    tous_routeurs = []
    for line in data.decode().splitlines():
        if line == "END":
            break
        ip, port, n, e = line.split()
        tous_routeurs.append((ip, int(port), (int(n), int(e))))
    # Après récupération
    print(f"[CLIENT] Routeurs récupérés: {tous_routeurs}")

    # Sélectionner aléatoirement 3 routeurs (ou moins si moins de 3 disponibles) (le circuit)
    num_routeurs = min(3, len(tous_routeurs))
    # circuit = tous_routeurs[:3] if len(tous_routeurs) >= 3 else tous_routeurs
    circuit = random.sample(tous_routeurs, num_routeurs) if num_routeurs > 0 else []
    print(f"[CLIENT] Circuit sélectionné: {circuit}")

    if not circuit:
        print("[CLIENT] Erreur: Aucun routeur disponible pour le circuit.")
        return

    oignon = build_oignon(message, circuit)
    print(f"[CLIENT] Oignon construit: {oignon[:100]}...")

    if circuit :
        first_ip, first_port, _ = circuit[0]
        print(f"[CLIENT] Tentative de connexion à {first_ip}:{first_port}")
        sock = socket.socket()
        sock.connect((first_ip, first_port))
        sock.sendall(oignon)
        sock.close()
        print("[CLIENT] Message envoyé")

# client B / récepteur final
def start_client_b(port):
    s = socket.socket()
    s.bind(("127.0.0.1", port))
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
    parser.add_argument("--role", choices=["routeur", "clienta", "clientb"], required=True)
    parser.add_argument("--port", type=int)
    parser.add_argument("--msg")
    args = parser.parse_args()

    if args.role == "routeur":
        start_router(args.port)

    if args.role == "clienta":
        start_client_a(args.msg.encode())

    if args.role == "clientb":
        start_client_b(args.port)


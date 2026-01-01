import socket
import threading
import argparse
import random
import os
import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COMMUN_DIR = os.path.abspath(os.path.join(BASE_DIR, "../commun"))
sys.path.insert(0, COMMUN_DIR)
from crypto import (generate_keypair,
                    encrypt, serialize, # client
                    decrypt, deserialize) # routeur

MASTER_IP = "192.168.x.10"
MASTER_PORT = 5000
ROUTEUR_IP = "192.168.x.20"
CLIENT_B_IP = "192.168.x.20"
CLIENT_B_PORT = 6000

# routeur
def start_router(port):
    pub, priv = generate_keypair()
    print(f"[ROUTEUR {port}] Clé publique = {pub}")

    # socket REGISTER au master
    s = socket.socket()
    s.connect((MASTER_IP, MASTER_PORT))
    msg = f"REGISTER {ROUTEUR_IP} {port} {pub[0]}"
    s.sendall(msg.encode())
    s.close()

    # socket d'écoute
    server = socket.socket()
    server.bind(("0.0.0.0", port))
    server.listen()

    def handle(conn):
        data = b""
        while True:
            chunk = conn.recv(65536)
            if not chunk:
                break
            data += chunk
            if len(chunk) < 65536:
                break
        if not data:
            conn.close()
            return

        print(f"[ROUTEUR {port}] Paquet reçu")

        try:
            # étape 1 : déchiffrement du payload
            plain = decrypt(priv, data)

            # étape 2 : Gestion d'erreur pour le split
            if b"|" not in plain:
                print(f"[ROUTEUR {port}] Erreur: Pas de séparateur '|' dans plain: {plain}")
                conn.close()
                return

            # étape 3 : extraction destination + payload (Parsing destination)
            dest, payload = plain.split(b"|", 1)
            try:
                ip, port_str = dest.decode('utf-8').split(":")
                dest_port = int(port_str)
            except (UnicodeDecodeError, ValueError) as e:
                print(f"[ROUTEUR {port}] Erreur de décodage dest: {e}, dest: {dest}")
                conn.close()
                return

            # log
            print(f"[ROUTEUR {port}] Forward à {ip}:{dest_port}, payload: {payload[:50]}...")

            # étape 4 : forward
            forward = socket.socket()
            forward.connect((ip, dest_port))
            forward.sendall(payload)
            forward.close()
            print(f"[ROUTEUR {port}] Forward réussi à {ip}:{dest_port}")
        except Exception as e:
            print(f"[ROUTEUR {port}] Erreur: {e}")
        conn.close()

    while True:
        conn, _ = server.accept()
        threading.Thread(target=handle, args=(conn,), daemon=True).start()



# client A / construction oignon
MIN_HOPS = 3
MAX_HOPS = 4

def build_oignon(message: bytes, circuit):
    """
    # circuit = [R1, R2, R3] - ordre du chemin à parcourir
    # Construction de l'intérieur vers l'extérieur
    #
    # R3 déchiffre et trouve : dest=ClientB | message
    # R2 déchiffre et trouve : dest=R3 | payload_chiffré_pour_R3
    # R1 déchiffre et trouve : dest=R2 | payload_chiffré_pour_R2
    """
    # début : message destiné au Client B (dernière destination)
    payload = f"{CLIENT_B_IP}:{CLIENT_B_PORT}|".encode() + message
    
    # parcours du dernier au premier routeur
    for i in range(len(circuit) - 1, -1, -1):
        ip, port, pubkey = circuit[i]
        print(f"\n[CLIENT] Chiffrement couche {len(circuit) - i} pour routeur {ip}:{port}")
        
        # chiffrement du payload actuel (qui contient déjà dest|data)
        payload = serialize(encrypt(pubkey, payload))
        
        # si ce n'est pas le premier routeur, préparation de la couche pour le routeur précédent
        if i > 0:
            # préfixe avec la destination (routeur actuel) pour le prochain chiffrement
            next_dest = f"{ip}:{port}|".encode()
            payload = next_dest + payload
    return payload

def start_client_a(message: bytes):
    s = socket.socket()
    s.connect((MASTER_IP, MASTER_PORT))
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
        ip, port, pubkey = line.split()
        tous_routeurs.append((ip, int(port), (int(pubkey),)))
    print(f"\n[CLIENT] Routeurs récupérés: {tous_routeurs}")

    # sélection aléatoirement de 3 routeurs min
    if len(tous_routeurs) < MIN_HOPS:
        print("[CLIENT] Pas assez de routeurs disponibles")
        return
    nb_sauts = random.randint(
        MIN_HOPS,
        min(MAX_HOPS, len(tous_routeurs))
    )
    circuit = random.sample(tous_routeurs, nb_sauts)
    print(f"\n[CLIENT] Circuit sélectionné: {[f'{ip}:{port}' for ip, port, _ in circuit]}")

    if not circuit:
        print("[CLIENT] Erreur: Aucun routeur disponible pour le circuit.")
        return

    oignon = build_oignon(message, circuit)
    print(f"\n[CLIENT] Oignon construit: {oignon[:100]}...")

    if circuit :    # logique Tor-like (entrée du circuit)
        first_ip, first_port, _ = circuit[0]
        print(f"\n[CLIENT] Tentative de connexion à {first_ip}:{first_port}")
        sock = socket.socket()
        sock.connect((first_ip, first_port))
        sock.sendall(oignon)
        sock.close()
        print("\n[CLIENT] Message envoyé")

# client B / récepteur comm_fonctionnelle
def start_client_b(port):
    s = socket.socket()
    s.bind(("0.0.0.0", port))
    s.listen()
    print("[CLIENT B] Écoute")

    def handle(conn):
        data = conn.recv(4096)
        msg = data.decode("utf-8", errors="replace")
        if msg:
            print("[CLIENT B] Message reçu :", msg)
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


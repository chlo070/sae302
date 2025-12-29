import socket
import threading
import argparse
import random
import sys
sys.path.append("../commun")
from crypto import (generate_keypair,
                    encrypt, serialize, # client
                    decrypt, deserialize) # routeur

CLIENT_B_IP = "127.0.0.1"
CLIENT_B_PORT = 6000

# routeur
def start_router(port):
    pub, priv = generate_keypair()
    print(f"[ROUTEUR {port}] Clé publique = {pub}")

    # socket REGISTER au master
    s = socket.socket()
    s.connect(("127.0.0.1", 4000))
    msg = f"REGISTER 127.0.0.1 {port} {pub[0]}"
    s.sendall(msg.encode())
    s.close()

    # socket d'écoute
    server = socket.socket()
    server.bind(("127.0.0.1", port))
    server.listen()

    def handle(conn):
        data = b""
        while True:
            chunk = conn.recv(65536)
            if not chunk:
                break
            data += chunk
            # Si on a reçu des données et pas de nouveau chunk, on sort
            if len(chunk) < 65536:
                break
        if not data:
            conn.close()
            return

        print(f"[ROUTEUR {port}] Paquet reçu")

        try:
            # étape 1 : déchiffrement du payload
            plain = decrypt(priv, data)
            print(f"[ROUTEUR {port}] Forward vers {ip}:{port}")
            # étape 2 : extraction destination + payload
            # Gestion d'erreur pour le split
            if b"|" not in plain:
                print(f"[ROUTEUR] Erreur: Pas de séparateur '|' dans plain: {plain}")
                conn.close()
                return
            dest, payload = plain.split(b"|", 1)
            try:
                ip, port_str = dest.decode('utf-8').split(":")
                port = int(port_str)
            except (UnicodeDecodeError, ValueError) as e:
                print(f"[ROUTEUR] Erreur de décodage dest: {e}, dest: {dest}")
                conn.close()
                return
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
MIN_HOPS = 3
MAX_HOPS = 4

def build_oignon(message: bytes, circuit):
    # circuit = [R1, R2, R3] - ordre du chemin à parcourir
    # Construction de l'intérieur vers l'extérieur
    # 
    # R3 déchiffre et trouve : dest=ClientB | message
    # R2 déchiffre et trouve : dest=R3 | payload_chiffré_pour_R3
    # R1 déchiffre et trouve : dest=R2 | payload_chiffré_pour_R2
    
    # Début : message destiné au Client B (dernière destination)
    payload = f"{CLIENT_B_IP}:{CLIENT_B_PORT}|".encode() + message
    
    # Parcours du dernier au premier routeur
    for i in range(len(circuit) - 1, -1, -1):
        ip, port, pubkey = circuit[i]
        print(f"[CLIENT] Chiffrement couche {len(circuit) - i} pour routeur {ip}:{port}")
        
        # Chiffrer le payload actuel (qui contient déjà dest|data)
        payload = serialize(encrypt(pubkey, payload))
        
        # Si on n'est pas au premier routeur, on doit préparer la couche pour le routeur précédent
        # Le routeur i-1 doit savoir envoyer vers le routeur i
        if i > 0:
            # On préfixe avec la destination (routeur actuel) pour le prochain chiffrement
            next_dest = f"{ip}:{port}|".encode()
            payload = next_dest + payload
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
        ip, port, pubkey = line.split()
        tous_routeurs.append((ip, int(port), (int(pubkey),)))
    # Après récupération
    print(f"[CLIENT] Routeurs récupérés: {tous_routeurs}")

    # Sélectionner aléatoirement 3 routeurs au minimum
    if len(tous_routeurs) < MIN_HOPS:
        print("[CLIENT] Pas assez de routeurs disponibles")
        return
    nb_sauts = random.randint(
        MIN_HOPS,
        min(MAX_HOPS, len(tous_routeurs))
    )
    circuit = random.sample(tous_routeurs, nb_sauts)    # nombre aléatoire
    print(f"[CLIENT] Circuit sélectionné: {circuit}")

    if not circuit:
        print("[CLIENT] Erreur: Aucun routeur disponible pour le circuit.")
        return

    oignon = build_oignon(message, circuit)
    print(f"[CLIENT] Oignon construit: {oignon[:100]}...")

    if circuit :    # logique Tor-like (entrée du circuit)
        first_ip, first_port, _ = circuit[0]
        print(f"[CLIENT] Tentative de connexion à {first_ip}:{first_port}")
        sock = socket.socket()
        sock.connect((first_ip, first_port))
        sock.sendall(oignon)
        sock.close()
        print("[CLIENT] Message envoyé")

    print(f"[CLIENT] Circuit final : {[f'{ip}:{port}' for ip, port, _ in circuit]}")

# client B / récepteur comm_fonctionnelle
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


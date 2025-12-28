import socket
import threading
from crypto import generate_keypair, decrypt

HOST = "127.0.0.1"
PORT = 5002
NEXT_HOP = ("127.0.0.1", 5003)  # routeur suivant ou Client B


# génération clé privée/clé publique
pub, priv = generate_keypair()
print("[ROUTEUR] Clé publique =", pub)

def handle_client(conn):
    try:
        # --- RÉCEPTION ---
        data = conn.recv(4096)
        if not data:
            conn.close()
            return # ignore paquets vides
        else:
            print("[ROUTEUR] Cipher reçu (bytes) :", data))


        # --- DECRYPTAGE RSA ---
        # 1) conversion bytes -> entier
        cipher = int.from_bytes(data, "big")

        # 2) déchiffrement RSA
        plain = decrypt(priv, cipher)
        print("[ROUTEUR] Déchiffré :", plain)

        # --- FORWARD ---
        # 3) forward du message déchiffré vers NEXT_HOP
        forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        forward.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        forward.connect(NEXT_HOP)
        forward.sendall(plain)
        forward.close()

    except Exception as e:
        print("Erreur routeur:", e)

    finally:
        conn.close()

def start_router():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))

    # Timeout pour capturer Ctrl+C
    s.settimeout(1.0)  # timeout de 1 seconde sur accept()
    s.listen()
    print("[ROUTEUR] Écoute sur", PORT)
    try:
        while True:
            try:
                conn, addr = s.accept()
                threading.Thread(target=handle_client, args=(conn,), daemon=True).start()
            except socket.timeout:
                # on revient dans la boucle, ce qui permet de capter Ctrl+C
                continue
    except KeyboardInterrupt:
        print("\n[ROUTEUR] Arrêt demandé par l'utilisateur.")
    finally:
        s.close()
        print("[ROUTEUR] Socket fermé.")
    #while True:
        #conn, addr = s.accept()
        #threading.Thread(target=handle_client, args=(conn,)).start()

"""
def cryptage(): # inutile finalement
    data = conn.recv(4096)
    cipher = int.from_bytes(data, "big")  # réception du nombre
    plain = decrypt(priv, cipher)
    print("[ROUTEUR] Déchiffré :", plain)
    conn.close()
"""

if __name__ == "__main__":
    start_router()

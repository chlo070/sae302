import socket
from protCrypto import generate_keypair, decrypt

HOST = "127.0.0.1"
PORT = 5002

# génération clé privée/clé publique
pub, priv = generate_keypair()
print("[ROUTEUR] Clé publique =", pub)

s = socket.socket()
s.bind((HOST, PORT))
s.listen()
print("[ROUTEUR] Écoute sur", PORT)

while True:
    conn, addr = s.accept()
    data = conn.recv(4096)
    cipher = int.from_bytes(data, "big")  # réception du nombre
    plain = decrypt(priv, cipher)
    print("[ROUTEUR] Déchiffré :", plain)
    conn.close()

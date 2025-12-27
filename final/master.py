import socket

HOST = "127.0.0.1"
PORT = 4000

routeurs = {}  # clé = (ip, port), valeur = clé publique

def start_master():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print("[MASTER] En écoute")
 
    while True:
        conn, _ = s.accept()
        data = conn.recv(4096).decode().strip()

        if data.startswith("REGISTER"):
            _, ip, port, pubkey = data.split()
            key = (ip, int(port))
            routeurs[key] = int(pubkey)
            print(f"[MASTER] Routeur enregistré: {ip}:{port}")

        elif data == "GET_CIRCUIT":
            for (ip, port), pubkey in routeurs.items():
                conn.sendall(f"{ip} {port} {pubkey}\n".encode())
            conn.sendall(b"END\n")

        conn.close()

if __name__ == "__main__":
    start_master()

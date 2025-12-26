import socket

HOST = "127.0.0.1"
PORT = 4000

routeurs = {}  # Changé en dict pour éviter les doublons : clé = (ip, port), valeur = (n, e)

def start_master():
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen()
    print("[MASTER] En écoute")

    while True:
        conn, _ = s.accept()
        data = conn.recv(4096).decode().strip()

        if data.startswith("REGISTER"):
            _, ip, port, n, e = data.split()
            key = (ip, int(port))
            routeurs[key] = (int(n), int(e))  # update ou ajoute
            print(f"[MASTER] Routeur enregistré/mis à jour: {ip}:{port}")


        elif data == "GET_CIRCUIT":
            for (ip, port), (n, e) in routeurs.items():
                conn.sendall(f"{ip} {port} {n} {e}\n".encode())
            conn.sendall(b"END\n")

        conn.close()

if __name__ == "__main__":
    start_master()

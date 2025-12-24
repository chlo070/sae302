import socket

HOST = "127.0.0.1"
PORT = 4000


routeurs = []

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
            routeurs.append((ip, int(port), int(n), int(e)))
            print("[MASTER] Routeur enregistré", ip, port)

        elif data == "GET_CIRCUIT":
            for r in routeurs:
                conn.sendall(f"{r[0]} {r[1]} {r[2]} {r[3]}\n".encode())
            conn.sendall(b"END\n")

        conn.close()

if __name__ == "__main__":
    start_master()

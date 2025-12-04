import socket
import threading
import argparse


def handle_client(conn):
    data = conn.recv(4096)
    if data:
        print("[CLIENT B] Message reçu :", data.decode("utf-8"))
    conn.close()

def start_client_b(port):
    s = socket.socket()
    s.bind(("0.0.0.0", port))
    s.listen()
    s.settimeout(1.0)  # timeout de 1 seconde sur accept()

    print(f"[CLIENT B] Écoute sur {port}")
    try:
        while True:
            try:
                conn, addr = s.accept()
                threading.Thread(target=handle_client, args=(conn,)).start()
            except socket.timeout:
                # on revient dans la boucle, ce qui permet de capter Ctrl+C
                continue
    except KeyboardInterrupt:
        print("\n[CLIENT B] Arrêt demandé par l'utilisateur.")
    finally:
        s.close()
        print("[CLIENT B] Socket fermé.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()
    start_client_b(args.port)

import socket
import threading

ROUTER_PORT = 5002
NEXT_HOP = ("127.0.0.1", 5003)  # routeur suivant ou Client B


def handle_client(conn):
    try:
        data = conn.recv(4096)
        print("Routeur a reçu:", data)

        forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        forward.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        forward.connect(NEXT_HOP)
        forward.sendall(data)
        forward.close()

    except Exception as e:
        print("Erreur routeur:", e)

    finally:
        conn.close()

def start_router():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # limite les requêtes
    s.bind(("127.0.0.1", ROUTER_PORT))

    # Timeout pour capturer Ctrl+C
    s.settimeout(1.0)  # timeout de 1 seconde sur accept()
    s.listen()
    print(f"Routeur connecté sur {ROUTER_PORT}")
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

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn,)).start()


if __name__ == "__main__":
    start_router()
import socket
import pickle

HOST = "127.0.0.1"
PORT = 4000

# circuit statique pour MVP
# à terme : dynamique
ROUTERS = [
    ("127.0.0.1", 5001),
    ("127.0.0.1", 5002),
    ("127.0.0.1", 5003),
]

def start_master():
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen()
    print("[MASTER] En écoute")

    while True:
        conn, _ = s.accept()
        conn.sendall(pickle.dumps(ROUTERS))
        conn.close()

if __name__ == "__main__":
    start_master()

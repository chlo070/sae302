import socket
import threading
import argparse
import pickle
from rsa import generate_keypair, encrypt, decrypt

MASTER_ADDR = ("127.0.0.1", 4000)

def start_router(port):
    pub, priv = generate_keypair()
    print(f"[ROUTER {port}] Clé générée")

    s = socket.socket()
    s.bind(("127.0.0.1", port))
    s.listen()

    def handle(conn):
        data = conn.recv(4096)
        if not data:
            conn.close()
            return

        plain = decrypt(priv, data)
        header, payload = plain.split(b"|", 1)

        if header == b"END":
            print("[MESSAGE FINAL]", payload)
        else:
            ip, p = header.decode().split(":")
            forward = socket.socket()
            forward.connect((ip, int(p)))
            forward.sendall(payload)
            forward.close()

        conn.close()

    while True:
        conn, _ = s.accept()
        threading.Thread(target=handle, args=(conn,), daemon=True).start()

def start_client(message: bytes):
    s = socket.socket()
    s.connect(MASTER_ADDR)
    routers = pickle.loads(s.recv(4096))
    s.close()

    payload = b"END|" + message

    for ip, port in reversed(routers):
        pub = RSA_KEYS[(ip, port)]
        payload = encrypt(pub, f"{ip}:{port}|".encode() + payload)

    first = routers[0]
    sock = socket.socket()
    sock.connect(first)
    sock.sendall(payload)
    sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", choices=["router", "client"], required=True)
    parser.add_argument("--port", type=int)
    parser.add_argument("--msg")
    args = parser.parse_args()

    if args.role == "router":
        start_router(args.port)

    if args.role == "client":
        start_client(args.msg.encode())

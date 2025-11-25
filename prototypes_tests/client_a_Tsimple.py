import socket
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5002)
    parser.add_argument("--msg", required=True, help="Message à envoyer")
    args = parser.parse_args()

    HOST = args.host
    PORT = args.port
    MESSAGE = args.msg.encode("utf-8")

    s = socket.socket()
    s.connect((HOST, PORT))
    s.sendall(MESSAGE)
    s.close()

    print(f"[CLIENT A] Message envoyé avec succès : {args.msg}")
    print("Connexion au serveur fermée")


if __name__ == "__main__":
    main()
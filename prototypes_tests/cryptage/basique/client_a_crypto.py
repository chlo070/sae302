import socket
import argparse
from protCrypto import encrypt, generate_keypair

"""
# Clé publique du routeur : recopier celle affichée dans router_crypto.py
ROUTER_PUB = (3233, 17)   # EXEMPLE, à remplacer !


msg = b"hello routeur"
cipher = encrypt(ROUTER_PUB, msg)

s.connect(("0.0.0.0", 5002))
s.sendall(cipher.to_bytes((cipher.bit_length()+7)//8, "big"))
s.close()
"""

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
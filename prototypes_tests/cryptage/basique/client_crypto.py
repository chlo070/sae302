import socket
from protCrypto import encrypt, generate_keypair

# Clé publique du routeur : recopier celle affichée dans router_crypto.py
ROUTER_PUB = (3233, 17)   # EXEMPLE, à remplacer !

msg = b"hello routeur"
cipher = encrypt(ROUTER_PUB, msg)

s = socket.socket()
s.connect(("127.0.0.1", 5002))
s.sendall(cipher.to_bytes((cipher.bit_length()+7)//8, "big"))
s.close()

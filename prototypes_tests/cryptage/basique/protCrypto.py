# crypto_proto.py (RSA jouet minimal)

import random

def generate_keypair():
    p, q = 10007, 10009 # petits nombres pour démonstration
                  # (pas sécurisés -> dans un vrai RSA c'est 1024+bits)
    n = p * q     # module RSA
    phi = (p - 1) * (q - 1) # calcul clé privée (reste secrète en théorie RSA)
    e = 17 # exposant public exemple (mais en gal. 65537)
    # calcul d = inverse de e mod phi
    # d = inverse_modulaire(e, phi)
    d = pow(e, -1, phi)
    return (n, e), (n, d) # clé pub, clé priv

def encrypt(pub, msg: bytes):
    n, e = pub # extraire la clé publique
    m = int.from_bytes(msg, "big") # conversion du message en un gros entier
                                            # (RSA ne chiffre que des nombres)
    c = pow(m, e, n) # Chiffrement RSA : c= m^e mod n
    return c # sous forme de nombre entier (pas de bytes)

def decrypt(priv, c: int):
    n, d = priv # récupérer la clé privée
    m = pow(c, d, n) # DEchiffrement RSA : c= m^e mod n
    # récupération du message initial -> reconvertion de m en bytes
    return m.to_bytes((m.bit_length() + 7)//8, "big")

import random
import math
from sympy import isprime

# génération nombres premiers
def generate_prime(bits=16):
    while True:
        candidate = random.getrandbits(bits)
        if candidate % 2 == 0:
            continue
        if isprime(candidate):
            return candidate

# inverse modulaire
def egcd(a, b):
    if a == 0:
        return b, 0, 1
    g, y, x = egcd(b % a, a)
    return g, x - (b // a) * y, y

def modinv(a, m):
    g, x, _ = egcd(a, m)
    if g != 1:
        raise Exception("Inverse modulaire impossible")
    return x % m

# génération paire de clés
def generate_keypair(bits=16):
    p = generate_prime(bits)
    q = generate_prime(bits)
    while p == q:
        q = generate_prime(bits)

    n = p * q   # module RSA
    phi = (p - 1) * (q - 1) # calcul clé privée

    e = random.randrange(3, phi, 2)
    while math.gcd(e, phi) != 1:
        e = random.randrange(3, phi, 2)

    d = modinv(e, phi)

    return (n, e), (n, d)   # clé pub, clé priv

def encrypt(pubkey, message: bytes):    # chiffrement
    n, e = pubkey
    for b in message:   # vérification taille des blocs/caractères
        if b >= n:
            raise ValueError("Bloc trop grand pour n")
    return [pow(b, e, n) for b in message]

def decrypt(privkey, cipher_blocks):    # déchiffrement
    n, d = privkey
    # return bytes([pow(c, d, n) for c in cipher_blocks])   # obsolète car interdit les message trop gros
    return " ".join(str(pow(c, d, n)) for c in cipher_blocks).encode()  # chaine de texte comme pour 'serialize'

# sérialisation
def serialize(blocks):
    return " ".join(str(b) for b in blocks).encode()

def deserialize(data):
    return [int(x) for x in data.decode().split()]



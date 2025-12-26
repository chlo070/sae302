import random
import math
from sympy import isprime

# génération nombres premiers
def generate_prime(bits=512):
    while True:
        candidat = random.getrandbits(bits)
        if candidat % 2 == 0:
            continue
        if isprime(candidat):
            return candidat

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
def generate_keypair(bits=512):
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

def encrypt(pubkey, message: bytes):    # chiffrement par blocs
    n, e = pubkey
    blocks = []
    for i in range(0, len(message), 128):
        block = message[i:i+128].ljust(128, b'\x00')  # Pad avec \x00 si < 32 bytes
        block_int = int.from_bytes(block, 'big')
        if block_int >= n:
            raise ValueError("Bloc trop grand pour n")
        blocks.append(pow(block_int, e, n))
    return blocks
 
def decrypt(privkey, cipher_blocks):    # déchiffrement par blocs de 32 bytes
    n, d = privkey
    decrypted = []
    for c in cipher_blocks:
        val = pow(c, d, n)
        block_bytes = val.to_bytes(128, 'big').lstrip(b'\x00')  # Enlève le padding \x00
        decrypted.extend(block_bytes)
    return bytes(decrypted)

# sérialisation
def serialize(blocks):
    return " ".join(str(b) for b in blocks).encode()

def deserialize(data):
    try:
        return [int(x) for x in data.decode().split()]
    except ValueError as e:
        raise ValueError(f"Erreur de désérialisation: {e}. Données reçues: {data[:100]}...")
# Toy RSA minimal pour usage pédagogique / MVP.
# - génère des p, q par tests de primalité Miller-Rabin
# - expose generate_keypair(bit_size=512)
# - encrypt_with_pub(pub, plaintext_bytes) -> ciphertext_bytes
# - decrypt_with_priv(priv, ciphertext_bytes) -> plaintext_bytes
#
# AVERTISSEMENT : ce RSA est didactique, pas sécurisé pour un usage réel.

import secrets
import math

# ---------- utilitaires ----------
def _int_to_bytes(x: int) -> bytes:
    if x == 0:
        return b"\x00"
    length = (x.bit_length() + 7) // 8
    return x.to_bytes(length, byteorder="big")

def _bytes_to_int(b: bytes) -> int:
    return int.from_bytes(b, byteorder="big")

def _egcd(a, b):
    if b == 0:
        return (1, 0, a)
    x1, y1, g = _egcd(b, a % b)
    return (y1, x1 - (a // b) * y1, g)

def _modinv(a, m):
    x, y, g = _egcd(a, m)
    if g != 1:
        raise ValueError("Inverse modulaire impossible")
    return x % m

# ---------- primalité (Miller-Rabin) ----------
def _is_probable_prime(n, rounds=8):
    if n < 2:
        return False
    small_primes = [2,3,5,7,11,13,17,19,23,29]
    for p in small_primes:
        if n % p == 0:
            return n == p
    # write n-1 as d*2^s
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(rounds):
        a = secrets.randbelow(n - 3) + 2  # random in [2, n-2]
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        composite = True
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                composite = False
                break
        if composite:
            return False
    return True

def _generate_prime_candidate(bits):
    # generate an odd candidate of given bit length with top bit set
    candidate = secrets.randbits(bits)
    candidate |= (1 << (bits - 1))  # ensure top bit to get desired size
    candidate |= 1  # make odd
    return candidate

def _generate_prime(bits):
    while True:
        candidate = _generate_prime_candidate(bits)
        if _is_probable_prime(candidate, rounds=10):
            return candidate

# ---------- API ----------
def generate_keypair(bit_size=512):
    """
    Génère une paire (pub, priv).
    pub = {'n': n, 'e': e}
    priv = {'n': n, 'd': d}
    bit_size : taille approximative de n en bits (p et q seront ~bit_size/2)
    """
    if bit_size < 128:
        raise ValueError("bit_size trop petit")
    half = bit_size // 2
    p = _generate_prime(half)
    q = _generate_prime(half)
    # s'assurer que p != q
    while q == p:
        q = _generate_prime(half)

    n = p * q
    phi = (p - 1) * (q - 1)

    # choix d'e : petit et impair, habituellement 65537
    e = 65537
    # si e n'est pas coprime avec phi, choisir autre e
    if math.gcd(e, phi) != 1:
        # tomber en fallback simple
        e = 3
        while math.gcd(e, phi) != 1:
            e += 2

    d = _modinv(e, phi)

    pub = {"n": n, "e": e}
    priv = {"n": n, "d": d}
    return pub, priv

def encrypt_with_pub(pub, plaintext_bytes):
    """
    Chiffrement RSA basique avec blocage.
    - pub['n'], pub['e'] attendus.
    - On segmente le message en blocs de taille b = floor((n.bit_length()-1)/8)
      afin de s'assurer que m < n.
    - Retourne la concaténation des blocs chiffrés, chaque bloc codé sur k bytes
      où k = ceil(n.bit_length()/8).
    """
    n = pub["n"]
    e = pub["e"]
    k = (n.bit_length() + 7) // 8 # taille en bytes d'un bloc chiffré
    b = (n.bit_length() - 1) // 8 # taille max de bloc en bytes pour m < n

    if b <= 0:
        raise ValueError("Module trop petit pour l'encodage")

    out = bytearray()
    # découpe en blocs
    for i in range(0, len(plaintext_bytes), b):
        chunk = plaintext_bytes[i:i + b]
        m = _bytes_to_int(chunk)
        if m >= n:
            raise ValueError("Bloc message >= n (impossible)")
        c = pow(m, e, n)
        c_bytes = c.to_bytes(k, byteorder="big")
        out.extend(c_bytes)
    return bytes(out)

def decrypt_with_priv(priv, ciphertext_bytes):
    """
    Déchiffrement RSA correspondant.
    - priv['n'], priv['d'] attendus.
    - On découpe le ciphertext en blocs de taille k = ceil(n.bit_length()/8),
      on applique pow(c,d,n) et on reconstruit le message concaténé.
    """
    n = priv["n"]
    d = priv["d"]
    k = (n.bit_length() + 7) // 8
    if k <= 0:
        raise ValueError("Module invalide")

    if len(ciphertext_bytes) % k != 0:
        raise ValueError("Taille du ciphertext inattendue (doit être multiple de k)")

    out = bytearray()
    for i in range(0, len(ciphertext_bytes), k):
        c_chunk = ciphertext_bytes[i:i + k]
        c = _bytes_to_int(c_chunk)
        m = pow(c, d, n)
        m_bytes = _int_to_bytes(m)
        out.extend(m_bytes)
    return bytes(out)

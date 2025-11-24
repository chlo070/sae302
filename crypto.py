# Module de chiffrement simplifié pour le MVP.
# Fournit une API : generate_keypair(), encrypt_with_pub(), decrypt_with_priv()
# -------------------------------------------------------------------

def generate_keypair():
    """
    Génère une paire clé publique / clé privée.
    Pour le MVP : tu peux faire un toy RSA, ou même un chiffrement XOR avec clé.
    Retourne (pub, priv)
    """
    pub = None
    priv = None
    return pub, priv


def encrypt_with_pub(pub, plaintext_bytes):
    """
    Chiffre des données avec la clé publique.
    Doit retourner un tableau de bytes.
    """
    ciphertext = plaintext_bytes
    return ciphertext


def decrypt_with_priv(priv, ciphertext_bytes):
    """
    Déchiffre les données avec la clé privée.
    Retourne plaintext_bytes.
    """
    plaintext = ciphertext_bytes
    return plaintext

"""
Chiffrement asymétrique simple et léger
Basé sur Diffie-Hellman + XOR

Principe :
1. Chaque nœud a une clé privée (nombre secret) et une clé publique (g^privée mod p)
2. Pour chiffrer : on génère une clé éphémère, on calcule un secret partagé, on XOR le message
3. Pour déchiffrer : on recalcule le secret partagé avec sa clé privée, on XOR

Avantages : léger, rapide, pas de limite de taille de message
"""

import random
import hashlib

# Paramètres Diffie-Hellman (petits pour la simplicité, et suffisants pour un contexte pédagogique, pas de production)
# p = nombre premier, g = générateur
P = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74
G = 2

def generate_keypair():
    """Génère une paire de clés (publique, privée)"""
    # clé privée : nombre aléatoire
    private = random.randint(2, P - 2)
    # clé publique : g^private mod p
    public = pow(G, private, P)
    return (public,), (private,)  # format tuple pour compatibilité

def _derive_key(shared_secret: int, length: int) -> bytes:
    """Dérive une clé de la longueur voulue à partir du secret partagé"""
    key = b""
    counter = 0
    while len(key) < length:
        data = f"{shared_secret}{counter}".encode()
        key += hashlib.sha256(data).digest()
        counter += 1
    return key[:length]

def _xor_bytes(data: bytes, key: bytes) -> bytes:
    """XOR entre data et key (key est répétée si nécessaire)"""
    return bytes(d ^ key[i % len(key)] for i, d in enumerate(data))

def encrypt(pubkey: tuple, message: bytes) -> bytes:
    """
    Chiffre un message avec la clé publique du destinataire
    
    Retourne : clé_éphémère_publique (32 bytes) + message_chiffré
    """
    recipient_public = pubkey[0]
    
    # génération clé éphémère (comme dans ECIES)
    ephemeral_private = random.randint(2, P - 2)
    ephemeral_public = pow(G, ephemeral_private, P)
    
    # calcul du secret partagé : (pubkey_destinataire)^ephemeral_private mod p
    shared_secret = pow(recipient_public, ephemeral_private, P)
    
    # dérivation d'une clé de chiffrement
    encryption_key = _derive_key(shared_secret, len(message))
    
    # chiffrement avec XOR
    ciphertext = _xor_bytes(message, encryption_key)
    
    # return : clé publique éphémère (en bytes) + ciphertext
    ephemeral_bytes = ephemeral_public.to_bytes(32, 'big')
    return ephemeral_bytes + ciphertext

def decrypt(privkey: tuple, encrypted: bytes) -> bytes:
    """
    Déchiffre un message avec sa clé privée
    
    encrypted = clé_éphémère_publique (32 bytes) + message_chiffré
    """
    private = privkey[0]
    
    # extrait de la clé publique éphémère et le ciphertext
    ephemeral_public = int.from_bytes(encrypted[:32], 'big')
    ciphertext = encrypted[32:]
    
    # recalcul du secret partagé : (ephemeral_public)^private mod p
    shared_secret = pow(ephemeral_public, private, P)
    
    # dérivation de la même clé de chiffrement
    encryption_key = _derive_key(shared_secret, len(ciphertext))
    
    # déchiffrement avec XOR
    plaintext = _xor_bytes(ciphertext, encryption_key)
    
    return plaintext

def serialize(data: bytes) -> bytes:
    """Sérialise les données (ici, juste retourne les bytes tels quels)"""
    return data

def deserialize(data: bytes) -> bytes:
    """Désérialise les données"""
    return data


# Test rapide
if __name__ == "__main__":
    print("=== Test du chiffrement asymétrique léger ===\n")
    
    # génération des clés
    pub, priv = generate_keypair()
    print(f"Clé publique: {pub[0]}")
    print(f"Clé privée: {priv[0]}\n")
    
    # chiffrement d'un message
    message = b"Hello World! Ceci est un message secret."
    print(f"Message original: {message}")
    
    encrypted = encrypt(pub, message)
    print(f"Message chiffré: {encrypted[:50]}... ({len(encrypted)} bytes)")
    
    # déchiffrement
    decrypted = decrypt(priv, encrypted)
    print(f"Message déchiffré: {decrypted}")
    
    assert message == decrypted, "Erreur de déchiffrement!"
    print("\n✓ Test réussi!")


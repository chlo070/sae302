# 3 fonctions : générer une clé + chiffrer + déchiffrer
from prototypes_tests.cryptage.basique.protCrypto import generate_keypair, encrypt, decrypt

pub, priv = generate_keypair() # génération obvi

message = b"bonjour"
cipher = encrypt(pub, message)
plain = decrypt(priv, cipher)

print("Message original :", message)
print("Chiffré (nombre) :", cipher)
print("Déchiffré        :", plain)

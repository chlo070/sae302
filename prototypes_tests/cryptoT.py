import crypto

def test_roundtrip():
    pub, priv = crypto.generate_keypair(bit_size=512)
    msg = b"bonjour, ceci est un test long qui depasse la taille d'un bloc si necessaire " * 2
    ct = crypto.encrypt_with_pub(pub, msg)
    pt = crypto.decrypt_with_priv(priv, ct)
    assert pt == msg, "Roundtrip échoué"
    print("Roundtrip OK, len(msg)=", len(msg), "len(ct)=", len(ct))

if __name__ == "__main__":
    test_roundtrip()

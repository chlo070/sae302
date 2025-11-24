# utils.py
# -------------------------------------------------------------------
# Fonctions utilitaires : sérialisation JSON (bytes), parsing d'adresses.
# -------------------------------------------------------------------

import json

def serialize(obj):
    """Convertit un dict Python en bytes (utf-8)."""
    return json.dumps(obj).encode("utf-8")


def deserialize(data_bytes):
    """Convertit des bytes en dict Python."""
    return json.loads(data_bytes.decode("utf-8"))


def parse_addr(addr_str):
    """Transforme '127.0.0.1:5002' en ('127.0.0.1', 5002)."""
    host, port = addr_str.split(":")
    return host, int(port)

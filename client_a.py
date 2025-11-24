# client_a.py
# -------------------------------------------------------------------
# Client A :
#  - demande les clés des routeurs au Master
#  - construit l’oignon
#  - envoie la première couche au routeur d’entrée
# -------------------------------------------------------------------

import socket
import argparse
from utils import serialize, deserialize, parse_addr
import crypto

def get_routers(master_addr):
    host, port = parse_addr(master_addr)
    s = socket.socket()
    s.connect((host, port))
    s.sendall(serialize({"type": "request_keys"}))

    data = s.recv(65536)
    s.close()

    resp = deserialize(data)
    return resp["routers"]


def build_onion(message, route):
    """
    route : liste de routeurs [{addr, pubkey}, ...]
    On construit l'oignon à l'envers.
    """
    payload = message.encode("utf-8")

    for i in reversed(route):
        layer = {
            "dest": i["addr"],      # next hop
            "payload": payload.decode("utf-8")
        }
        layer_bytes = serialize(layer)
        payload = crypto.encrypt_with_pub(i["pubkey"], layer_bytes)

    return payload


def send_to_entry(entry_addr, onion_bytes):
    host, port = parse_addr(entry_addr)
    s = socket.socket()
    s.connect((host, port))
    s.sendall(onion_bytes)
    s.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", type=str, required=True)
    parser.add_argument("--entry", type=str, required=True)
    parser.add_argument("--msg", type=str, required=True)
    parser.add_argument("--dest", type=str, required=True)
    args = parser.parse_args()

    # récupération clés routeurs
    routers = get_routers(args.master)

    # route = [R1, R2] — pour MVP, on prend juste les 2 premiers
    route = routers[:2]
    # mais R2 doit avoir dest = client B
    route[-1]["addr"] = args.dest

    onion = build_onion(args.msg, route)
    send_to_entry(args.entry, onion)

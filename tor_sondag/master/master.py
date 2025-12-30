import socket
import mysql.connector  # Connecteur pour MariaDB/MySQL
from mysql.connector import Error

HOST = "0.0.0.0"
PORT = 4000
MIN_HOPS = 3
MAX_HOPS = 5


"""Gestion de la BDD"""

# Configuration de la base
CONFIG_BDD = {
    'host': '%',
    'user': 'toto',
    'password': 'toto',
    'database': 'tor_sondag'
}

# connexion à la base
def get_db_connection():
    try:
        conn = mysql.connector.connect(**CONFIG_BDD)
        return conn
    except Error as e:
        print(f"[MASTER] Erreur de connexion BDD: {e}")
        return None

# table des logs
def log_event(source, message):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO logs (source, message) VALUES (%s, %s)", (source, message))
            conn.commit()
        except Error as e:
            print(f"[MASTER] Erreur lors du logging: {e}")
        finally:
            conn.close()

# table enregistrement des routeurs
def register_router(ip, port, pubkey):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO routeurs (ip, port, pubkey) VALUES (%s, %s, %s)", (ip, port, pubkey))
            conn.commit()
            log_event("MASTER", f"Routeur enregistré: {ip}:{port}")
            print(f"[MASTER] Routeur enregistré: {ip}:{port}")
        except Error as e:
            print(f"[MASTER] Erreur lors de l'enregistrement: {e}")
            log_event("MASTER", f"Erreur enregistrement routeur {ip}:{port}: {e}")
        finally:
            conn.close()

# lecture de la table routeurs
def get_routers():
    conn = get_db_connection()
    routers = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT ip, port, pubkey FROM routeurs")
            rows = cursor.fetchall()
            for row in rows:
                ip, port, pubkey = row
                routers.append((ip, int(port), (int(pubkey),)))  # Format compatible avec le code existant
            log_event("MASTER", f"Circuit demandé: {len(routers)} routeurs récupérés")
        except Error as e:
            print(f"[MASTER] Erreur lors de la récupération des routeurs: {e}")
            log_event("MASTER", f"Erreur récupération routeurs: {e}")
        finally:
            conn.close()
    return routers


"""Execution du master"""

def start_master():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print("[MASTER] En écoute")
    log_event("MASTER", "Master démarré et en écoute")
 
    while True:
        conn, _ = s.accept()
        data = conn.recv(4096).decode().strip()

        if data.startswith("REGISTER"):
            try:
                _, ip, port, pubkey = data.split()
                register_router(ip, int(port),  int(pubkey))
            except ValueError as e:
                print(f"[MASTER] Erreur parsing REGISTER: {e}")
                log_event("MASTER", f"Erreur parsing REGISTER: {data}")

        elif data == "GET_CIRCUIT":
            routers = get_routers()
            for (ip, port), pubkey in routers:
                conn.sendall(f"{ip} {port} {pubkey}\n".encode())    # pubkey est un tuple, on prend le premier élément
            conn.sendall(b"END\n")

        conn.close()

if __name__ == "__main__":
    start_master()

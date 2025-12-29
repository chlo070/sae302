#!/bin/bash

cd "$(dirname "$0")"
echo "[MASTER] Démarrage du master..."
python3 master.py

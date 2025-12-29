#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: ./lancement_routeur.sh <port>"
    exit 1
fi

cd "$(dirname "$0")"
python3 noeud.py --role routeur --port "$1"

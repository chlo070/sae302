#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: ./lancement_clientb.sh <port>"
    exit 1
fi

cd "$(dirname "$0")"
python3 noeud.py --role clientb --port "$1"

#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: ./lancement_clienta.sh <message>"
    exit 1
fi

cd "$(dirname "$0")"
python3 noeud.py --role clienta --msg "$1"

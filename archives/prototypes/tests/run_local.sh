#!/bin/bash

python master.py --port 5000 &
sleep 0.5
python router.py --port 5001 --master 127.0.0.1:5000 &
sleep 0.5
python router.py --port 5002 --master 127.0.0.1:5000 &
sleep 0.5
python client_b.py --port 5003 &
sleep 0.5

python client_a.py --master 127.0.0.1:5000 --entry 127.0.0.1:5001 --msg "hello world" --dest 127.0.0.1:5003

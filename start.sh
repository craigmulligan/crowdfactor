#!/bin/bash

set -m # to make job control work
python worker.py &
gunicorn 'server:app' -b 0.0.0.0:8080 & 
fg %1 # gross!

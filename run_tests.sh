#!/bin/bash
source venv/bin/activate
export PYTHONPATH=src

python3 -m unittest "$@"


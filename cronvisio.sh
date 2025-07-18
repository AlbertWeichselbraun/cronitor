#!/usr/bin/env bash

source ./.venv/bin/activate
export PYTHONPATH=$PYTHONPATH:./src

python3 ./src/cronvisio/cli.py $1

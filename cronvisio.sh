#!/usr/bin/env bash

source ./venv/bin/activate
export PYTHONPATH=$PYTHONPATH:./src

python ./scripts/cronitor-client.py

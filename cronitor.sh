#!/usr/bin/env bash

source ./venv/bin/activate
export PYTHONPATH=$PYTHONPATH:./src/cronitor

python ./scripts/cronitor.py

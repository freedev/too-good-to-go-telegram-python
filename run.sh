#!/bin/bash

source ./.venv/bin/activate
TIMESTAMP=$(date "+%Y%m%d %H%M%S")
echo -n "$TIMESTAMP "
python3 main.py
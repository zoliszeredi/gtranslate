#! /usr/bin/env bash
set -e


python3 -mvenv venv
venv/bin/pip install -e .

echo "venv/bin/gtranslate -f <file> -l <lang>"

#! /usr/bin/env bash


virtualenv -p $(which python3) venv
venv/bin/pip install -e .
echo venv/bin/gtranslate -f <file> -l <lang>

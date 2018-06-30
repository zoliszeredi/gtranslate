#! /usr/bin/env bash
set -e

venvpath=${1:-venv}

python3 -mvenv ${venvpath}
${venvpath}/bin/pip install -e .

echo "Crashcourse"
echo ""
echo ". $venvpath/bin/activate # activate the venv"
echo "gtd # this starts the daemon"
echo "gtranslate -f <file> -l <lang> # this does the translation"

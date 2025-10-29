#!/usr/bin/env sh

VENV_DIR="venv"
VENV_BIN="$VENV_DIR/bin"
VENV_PIP="$VENV_BIN/pip"
VENV_PYTHON="$VENV_BIN/python"

PYTHON="python3"

if [ ! -d "$VENV_DIR" ]; then
    echo "🐍 Creating Python venv in '$VENV_DIR'..."
    $PYTHON -m venv $VENV_DIR
fi

echo "🔧 Installing current project in editable mode..."
$VENV_PIP install -e .

echo "🔧 Installing minimal dependencies..."
$VENV_PIP install colorama

$VENV_PYTHON flexycon.py setup
$VENV_PYTHON flexycon.py install

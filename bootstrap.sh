#!/usr/bin/env sh

VENV_DIR=".venv"
VENV_BIN="$VENV_DIR/bin"
VENV_PIP="$VENV_BIN/pip"
VENV_PYTHON="$VENV_BIN/python"

PYTHON="python3"

if [ ! -d "$VENV_DIR" ]; then
    echo "🐍 Creating Python venv in '$VENV_DIR'..."
    $PYTHON -m venv $VENV_DIR
fi

echo "🔧 Installing current project and dependencies..."
$VENV_PIP install -e .

$VENV_PYTHON flexycon.py setup
$VENV_PYTHON flexycon.py install

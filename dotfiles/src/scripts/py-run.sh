#!/usr/bin/env sh

SCRIPT_NAME="$(basename "$0")"
SCRIPT_MODULE="$(echo "$SCRIPT_NAME" | sed 's/-/_/g')"

PROJECT_DIR="$FLEXYCON_HOME"
VENV="$PROJECT_DIR/venv"
PYTHON="$VENV/bin/python"
TARGET_SCRIPT="$PROJECT_DIR/dotfiles/src/scripts/$SCRIPT_MODULE/main.py"

if [ ! -x "$PYTHON" ]; then
    echo "Error: Python not found at $PYTHON" >&2
    exit 1
fi

if [ ! -f "$TARGET_SCRIPT" ]; then
    echo "Error: Script not found: $TARGET_SCRIPT" >&2
    exit 1
fi

exec "$PYTHON" "$TARGET_SCRIPT" "$@"

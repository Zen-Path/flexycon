#!/usr/bin/env sh

PROJECT_DIR="$FLEXYCON_HOME"
PYTHON="$PROJECT_DIR/venv/bin/python"
TARGET_SCRIPT="$PROJECT_DIR/dotfiles/src/scripts/{{@@ _dotfile_key.lstrip("d_").lstrip("f_") @@}}/main.py"

if [ ! -x "$PYTHON" ]; then
    echo "Error: Python not found at '$PYTHON'" >&2
    exit 1
fi

if [ ! -f "$TARGET_SCRIPT" ]; then
    echo "Error: Script not found at '$TARGET_SCRIPT'" >&2
    exit 1
fi

exec "$PYTHON" "$TARGET_SCRIPT" "$@"

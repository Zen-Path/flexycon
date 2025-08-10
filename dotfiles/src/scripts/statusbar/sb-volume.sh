#!/bin/sh

PYTHON="$FLEXYCON_HOME/venv/bin/python"
TARGET_SCRIPT="$FLEXYCON_HOME/dotfiles/src/scripts/statusbar/sb_volume.py"

exec "$PYTHON" "$TARGET_SCRIPT" "$@"

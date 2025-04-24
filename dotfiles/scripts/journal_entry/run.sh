#!/usr/bin/env sh

base_dir="$FLEXYCON_HOME/dotfiles/scripts/journal_entry"
"$base_dir/venv/bin/python" "$base_dir/main.py" "$@"

#!/usr/bin/env sh

base_dir="$FLEXYCON_HOME/dotfiles/scripts/jsonc_to_json"
"$base_dir/venv/bin/python" "$base_dir/main.py" "$@"

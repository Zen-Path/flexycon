#!/usr/bin/env sh

base_dir="$FLEXYCON_HOME/dotfiles/scripts/git_logs"
"$base_dir/venv/bin/python" "$base_dir/main.py" "$@"

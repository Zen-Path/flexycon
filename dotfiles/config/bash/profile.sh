#!/usr/bin/env bash

if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi

[ -f "$XDG_CONFIG_HOME/shell/aliases.sh" ] && source "$XDG_CONFIG_HOME/shell/aliases.sh"

echo "$XDG_CONFIG_HOME/shell/aliases.sh"

# SHORTCUTS
# {{@@ "\n" @@}}{%@@ include 'config/shell/shortcuts.sh' @@%}

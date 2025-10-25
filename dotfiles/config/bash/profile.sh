#!/usr/bin/env bash

test -f ~/.profile && . ~/.profile
test -f ~/.bashrc && . ~/.bashrc

# Load aliases if they exist.
[ -f "$XDG_CONFIG_HOME/shell/aliases.sh" ] && source "$XDG_CONFIG_HOME/shell/aliases.sh"

# SHORTCUTS
# {{ @@ "\n" @@}}{% @@ include 'config/zsh/shortcuts.sh' @@%}

#!/usr/bin/env bash

if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi

# ALIASES
# {%@@ include 'config/shell/aliases.sh' @@%}

# USER FUNCTIONS
# {%@@ include 'config/zsh/functions.sh' @@%}

# SHORTCUTS
# {{@@ "\n" @@}}{%@@ include 'config/zsh/shortcuts.sh' @@%}

#!/usr/bin/env bash

if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi

# ALIASES
# {%@@ include 'config/shell/aliases.sh' @@%}

# USER FUNCTIONS
# {%@@ include 'config/shell/functions.sh' @@%}

# SHORTCUTS
# {{@@ "\n" @@}}{%@@ include 'config/shell/shortcuts.sh' ignore missing @@%}

#!/usr/bin/env zsh

# {{@@ header() @@}}

# NOTE: Leave an empty line after commented block for templating purposes.

# Enable colors and change prompt:
autoload -U colors && colors # Load colors

PS1="%B%{$fg[red]%}[%{$fg[magenta]%}%~%{$fg[red]%}]%{$reset_color%}$%b "
# For multi-user systems, use this:
# PS1="%B%{$fg[red]%}[%{$fg[yellow]%}%n%{$fg[green]%}@%{$fg[blue]%}%M %{$fg[magenta]%}%~%{$fg[red]%}]%{$reset_color%}$%b "

setopt autocd   # Automatically cd into typed directory.
stty stop undef # Disable ctrl-s to freeze terminal.
setopt interactive_comments

# History in cache directory:
HISTSIZE=100000
SAVEHIST=100000
HISTFILE="$XDG_CACHE_HOME/zsh/history"
setopt appendhistory

# Load aliases and shortcuts if existent.
[ -f "$XDG_CONFIG_HOME/shell/shortcuts.sh" ] && source "$XDG_CONFIG_HOME/shell/shortcuts.sh"
[ -f "$XDG_CONFIG_HOME/shell/aliases.sh" ] && source "$XDG_CONFIG_HOME/shell/aliases.sh"

# Basic auto/tab complete:
autoload -U compinit
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}'
zstyle ':completion:*' menu select
zmodload zsh/complist
compinit
_comp_options+=(globdots) # Include hidden files.

# vi mode
bindkey -v
export KEYTIMEOUT=1

# Use vim keys in tab complete menu:
bindkey -M menuselect 'h' vi-backward-char
bindkey -M menuselect 'k' vi-up-line-or-history
bindkey -M menuselect 'l' vi-forward-char
bindkey -M menuselect 'j' vi-down-line-or-history
bindkey -v '^?' backward-delete-char

# Edit line in vim with ctrl-e:
autoload edit-command-line
zle -N edit-command-line
bindkey '^e' edit-command-line
bindkey -M vicmd '^[[P' vi-delete-char
bindkey -M vicmd '^e' edit-command-line
bindkey -M visual '^[[P' vi-delete

# Change cursor shape for different vi modes.
function zle-keymap-select() {
    case $KEYMAP in
        vicmd) echo -ne '\e[1 q' ;;        # block
        viins | main) echo -ne '\e[5 q' ;; # beam
    esac
}
zle -N zle-keymap-select

function zle-line-init() {
    # Initiate `vi insert` as keymap (can be removed if `bindkey -V` has been set elsewhere)
    zle -K viins
    echo -ne "\e[5 q"
}
zle -N zle-line-init

# Use beam shape cursor on startup.
echo -ne '\e[5 q'

# Use beam shape cursor for each new prompt.
function preexec() {
    echo -ne '\e[5 q'
}

# USER FUNCTIONS

# {%@@ include 'config/zsh/functions.sh' @@%}

bindkey -s '^f' 'fzfopen\n'

# Set up fzf key bindings and fuzzy completion
if command -v fzf > /dev/null 2>&1; then
    source <(fzf --zsh)
fi

if command -v starship > /dev/null 2>&1; then
    eval "$(starship init zsh)"
fi

# Load syntax highlighting; should be last.
source "$(brew --prefix)/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"

#!/usr/bin/env sh

# {{@@ header() @@}}

# Shell profile. Runs on login. Environmental variables are set here.

# {%@@- if os == "darwin" +@@%}
# Add Homebrew to $PATH
PATH="/opt/homebrew/bin:/opt/homebrew/sbin:$PATH"
# {%@@- endif +@@%}

PATH="$PATH:$(find ~/.local/bin -type d | paste -sd ':' -)"
export PATH

unsetopt PROMPT_SP

export DOTDROP_PROFILE='{{@@ _vars["active_dotdrop_profile"] @@}}'

# DEFAULT PROGRAMS

export EDITOR='nvim'
export VISUAL='code'
export BROWSER='firefox'
export FILE_MANAGER='yazi'

# {%@@- if os == "linux" +@@%}
export STATUSBAR='dwmblocks'
# {%@@- endif +@@%}

# {%@@- if os == "darwin" +@@%}
export TERMINAL='kitty'
# {%@@- elif os == "linux" +@@%}
export TERMINAL='alacritty'
# {%@@- endif +@@%}

# FILES

## XDG dirs
export XDG_CONFIG_HOME="$HOME/.config"
export XDG_DATA_HOME="$HOME/.local/share"
export XDG_SRC_HOME="$HOME/.local/src"
export XDG_BIN_HOME="$HOME/.local/bin"
export XDG_CACHE_HOME="$HOME/.cache"

export XDG_DOCUMENTS_DIR="$HOME/Documents"
export XDG_DOWNLOAD_DIR="$HOME/Downloads"
export XDG_MUSIC_DIR="$HOME/Music"
export XDG_PICTURES_DIR="$HOME/Pictures"

# {%@@- if os == "darwin" +@@%}
export XDG_VIDEOS_DIR="$HOME/Movies"
# {%@@- elif os == "linux" +@@%}
export XDG_VIDEOS_DIR="$HOME/Videos"
# {%@@- endif +@@%}

export XDG_PUBLICSHARE_DIR="$HOME/Public"
export XDG_DESKTOP_DIR="$HOME/Desktop"

# {%@@- if os == "linux" +@@%}
export XDG_TEMPLATES_DIR="$HOME/"
# {%@@- endif +@@%}

## $HOME Clean-up
# {%@@- if os == "linux" +@@%}
export XINITRC="$XDG_CONFIG_HOME/x11/xinitrc"
# {%@@- endif -@@%}

export INPUTRC="$XDG_CONFIG_HOME/shell/inputrc"
export ZDOTDIR="$XDG_CONFIG_HOME/zsh"
export GNUPGHOME="$XDG_DATA_HOME/gnupg"
# export PASSWORD_STORE_DIR="$XDG_DATA_HOME/password-store"
# export CARGO_HOME="$XDG_DATA_HOME/cargo"
# export RUSTUP_HOME="$XDG_DATA_HOME/rustup"
export HISTFILE="$XDG_DATA_HOME/history"
export PYTHONSTARTUP="$XDG_CONFIG_HOME/python/startup.py"
export SQLITE_HISTORY="$XDG_DATA_HOME/sqlite_history"
export npm_config_cache="$XDG_CACHE_HOME/npm"
export TASKRC="$XDG_CONFIG_HOME/task/taskrc"
export LESSHISTFILE="/dev/null"
export GIT_CONFIG_GLOBAL="$XDG_CONFIG_HOME/git/config.ini"
export STARSHIP_CONFIG="$XDG_CONFIG_HOME/starship/starship.toml"
export DOOMDIR="$XDG_CONFIG_HOME/doom"

## Misc files
# {%@@- if "home" in profile +@@%}
export JOURNAL_HOME="$XDG_DOCUMENTS_DIR/Journal"
# {%@@- endif +@@%}
export FLEXYCON_HOME="$XDG_SRC_HOME/flexycon"

# PROGRAM SETTINGS

# {%@@- if os == "linux" +@@%}
export SUDO_ASKPASS="$HOME/.local/bin/dmenupass"
# {%@@- endif -@@%}
export BAT_THEME='gruvbox-dark'
# export PASTEL_COLOR_MODE='24bit'

# {%@@- if os == "linux" +@@%}
export _JAVA_AWT_WM_NONREPARENTING='1' # Fix for Java applications in dwm
# {%@@- endif -@@%}

# export MOZ_USE_XINPUT2='1' # Mozilla smooth scrolling/touchpads.

## Less
export LESSOPEN='| /usr/bin/highlight -O ansi %s 2>/dev/null'
export LESS='--RAW-CONTROL-CHARS --quit-if-one-screen'

## Fzf
export FZF_DEFAULT_COMMAND='fd . --hidden --no-ignore --exclude .cache --exclude .git/ --exclude node_modules/ --exclude .local/lib/ --exclude .local/share/cargo --exclude .local/share/rustup'
export FZF_DEFAULT_OPTS='--multi --extended'

export JAVA_HOME="/opt/homebrew/opt/openjdk"

## ENV SETTINGS

# {%@@- if os == "linux" +@@%}
[ ! -f "$XDG_CONFIG_HOME/shell/shortcuts.sh" ] && setsid user_shortcuts --renderer 'zsh' > /dev/null 2>&1
# {%@@- elif os == "darwin" +@@%}
[ ! -f "$XDG_CONFIG_HOME/shell/shortcuts.sh" ] && user_shortcuts --renderer 'zsh'
# {%@@- endif +@@%}

# {%@@- if os == "linux" +@@%}
# Start graphical server on user's current tty if not already running.
[ "$(tty)" = "/dev/tty1" ] && ! pidof -s Xorg > /dev/null 2>&1 && startx "$XINITRC"

# Switch escape and caps if tty and no passwd required:
sudo -n loadkeys "$XDG_DATA_HOME"/larbs/ttymaps.kmap 2> /dev/null
# {%@@- endif +@@%}

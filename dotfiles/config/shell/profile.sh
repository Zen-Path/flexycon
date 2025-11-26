#!/usr/bin/env sh

# {{@@ header() @@}}

# Shell profile. Runs on login. Environmental variables are set here.

# {%@@- if os == "darwin" +@@%}
# Add Homebrew to $PATH
PATH="/opt/homebrew/bin:/opt/homebrew/sbin:$PATH"
# {%@@- endif +@@%}

PATH="$PATH:$(find ~/.local/bin -type d | paste -sd ':' -)"
export PATH

# Bash doesn't support 'unsetopt'
# $SHELL could be '/usr/bin/bash' or 'C:\Program Files\Git\usr\bin\bash.exe'
# {%@@- if "bash" not in env['SHELL'] +@@%}
unsetopt PROMPT_SP
# {%@@- endif +@@%}

export DOTDROP_PROFILE='{{@@ _vars["active_dotdrop_profile"] @@}}'

# DEFAULT PROGRAMS

export EDITOR='nvim'
export VISUAL='code'
export BROWSER='firefox'
export FILE_MANAGER='yazi'

# {%@@- if os == "darwin" +@@%}
export TERMINAL='kitty'
# {%@@- elif os == "linux" +@@%}
export TERMINAL='alacritty'
# {%@@- endif +@@%}

# {%@@- if os == "linux" +@@%}
export STATUSBAR='dwmblocks'
# {%@@- endif +@@%}

# FILES

## XDG dirs
export XDG_CACHE_HOME="$HOME/.cache"
export XDG_CONFIG_HOME="$HOME/.config"
export XDG_BIN_HOME="$HOME/.local/bin"
export XDG_DATA_HOME="$HOME/.local/share"
export XDG_SRC_HOME="$HOME/.local/src"

export XDG_DESKTOP_DIR="$HOME/Desktop"
export XDG_DOCUMENTS_DIR="$HOME/Documents"
export XDG_DOWNLOAD_DIR="$HOME/Downloads"
export XDG_MUSIC_DIR="$HOME/Music"
export XDG_PICTURES_DIR="$HOME/Pictures"
export XDG_PUBLICSHARE_DIR="$HOME/Public"

# {%@@- if os == "darwin" +@@%}
export XDG_VIDEOS_DIR="$HOME/Movies"
# {%@@- elif os == "linux" +@@%}
export XDG_VIDEOS_DIR="$HOME/Videos"
export XDG_TEMPLATES_DIR="$HOME/"
# {%@@- endif +@@%}

## $HOME clean-up
# export CARGO_HOME="$XDG_DATA_HOME/cargo"
# export DOOMDIR="$XDG_CONFIG_HOME/doom"
export GIT_CONFIG_GLOBAL="$XDG_CONFIG_HOME/git/config.ini"
export GNUPGHOME="$XDG_DATA_HOME/gnupg"
export HISTFILE="$XDG_DATA_HOME/history"
export INPUTRC="$XDG_CONFIG_HOME/shell/inputrc"
export npm_config_cache="$XDG_CACHE_HOME/npm"
# export PASSWORD_STORE_DIR="$XDG_DATA_HOME/password-store"
export PYTHONSTARTUP="$XDG_CONFIG_HOME/python/startup.py"
# export RUSTUP_HOME="$XDG_DATA_HOME/rustup"
export SQLITE_HISTORY="$XDG_DATA_HOME/sqlite_history"
export STARSHIP_CONFIG="$XDG_CONFIG_HOME/starship/starship.toml"
# export TASKRC="$XDG_CONFIG_HOME/task/taskrc"
export ZDOTDIR="$XDG_CONFIG_HOME/zsh"

# {%@@- if os == "linux" +@@%}
export XINITRC="$XDG_CONFIG_HOME/x11/xinitrc"
# {%@@- endif +@@%}

## Misc files
export FLEXYCON_HOME="$XDG_SRC_HOME/flexycon"

# {%@@- if "home" in profile +@@%}
export JOURNAL_HOME="$XDG_DOCUMENTS_DIR/Journal"
# {%@@- endif +@@%}

# PROGRAM SETTINGS

export BAT_THEME='gruvbox-dark'
# export MOZ_USE_XINPUT2='1' # Mozilla smooth scrolling/touchpads
# export PASTEL_COLOR_MODE='24bit'

## Less
export LESS='--RAW-CONTROL-CHARS --quit-if-one-screen'
export LESSOPEN='| /usr/bin/highlight -O ansi %s 2>/dev/null'

# {%@@- if os == "windows" +@@%}
export LESSHISTFILE='-'
# {%@@- else +@@%}
export LESSHISTFILE='/dev/null'
# {%@@- endif +@@%}

## Fzf
# To troubleshoot, run: `eval $FZF_DEFAULT_COMMAND`
export FZF_DEFAULT_COMMAND='
# Common excludes
EXCLUDES=(
    --exclude .git/
    --exclude .venv/
    --exclude venv/
    --exclude __pycache__/
    --exclude "*.egg-info/"
    --exclude .mypy_cache/
    --exclude .pytest_cache/
    --exclude node_modules/
    --exclude .DS_Store
)

# Extra excludes if in $HOME
if [ "$PWD" = "$HOME" ]; then
    EXCLUDES+=(
        --exclude .cache/
        --exclude .config/nvim/plugged/
        --exclude .local/share/nvim/
        --exclude .local/lib/
        --exclude .gradle/
        --exclude .vscode/extensions/
        --exclude "Library/Application Scripts/"
        --exclude Library/Caches/
        --exclude Library/Containers/
        --exclude Library/Logs/
        --exclude "Library/Group Containers/"
        --exclude "Pictures/Photos Library.photoslibrary/"
    )
fi

fd . --hidden --no-ignore --max-depth 10 "${EXCLUDES[@]}"
'
export FZF_DEFAULT_OPTS='--multi --extended'

# Java
# {%@@- if os == "darwin" +@@%}
export JAVA_HOME='/opt/homebrew/opt/openjdk'
# {%@@- endif +@@%}

# {%@@- if os == "linux" +@@%}
export _JAVA_AWT_WM_NONREPARENTING='1' # Fix for Java applications in dwm
# {%@@- endif +@@%}

## ENV SETTINGS

# {%@@- if os == "linux" +@@%}
export SUDO_ASKPASS="$XDG_BIN_HOME/dmenupass"

# Start graphical server on user's current tty if not already running.
if [ "$(tty)" = "/dev/tty1" ] && ! pidof -s Xorg > /dev/null 2>&1; then
    startx "$XINITRC"
fi
# {%@@- endif +@@%}

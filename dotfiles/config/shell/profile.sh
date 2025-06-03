#!/usr/bin/env sh

# {{@@ header() @@}}

# Shell profile. Runs on login. Environmental variables are set here.

# Add Homebrew to $PATH
PATH="/opt/homebrew/bin:$PATH:/usr/local/bin"

PATH="$PATH:$(find ~/.local/bin -type d | paste -sd ':' -)"
export PATH

unsetopt PROMPT_SP

# {{@@ "\n" @@}}export DOTDROP_PROFILE={{@@ "'" + _vars["active_dotdrop_profile"] + "'" @@}}

# DEFAULT PROGRAMS

export EDITOR='nvim'
export GRAPHICAL_EDITOR='code'
export TERMINAL='kitty'
export BROWSER='firefox'
export FILE_MANAGER='yazi'

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
export XDG_VIDEOS_DIR="$HOME/Movies"

export XDG_PUBLICSHARE_DIR="$HOME/Public"
export XDG_DESKTOP_DIR="$HOME/Desktop"

## $HOME Clean-up
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
# {%@@ if "home" in profile +@@%}
export JOURNAL_HOME="$XDG_DOCUMENTS_DIR/Journal"
# {%@@ endif +@@%}
export FLEXYCON_HOME="$HOME/.local/src/flexycon"

# PROGRAM SETTINGS

export BAT_THEME='gruvbox-dark'
# export PASTEL_COLOR_MODE='24bit'

## Less
export LESSOPEN='| /usr/bin/highlight -O ansi %s 2>/dev/null'
export LESS='--RAW-CONTROL-CHARS --quit-if-one-screen'

## Fzf
export FZF_DEFAULT_COMMAND='fd . --hidden --no-ignore --exclude .cache --exclude .git/ --exclude node_modules/ --exclude .local/lib/ --exclude .local/share/cargo --exclude .local/share/rustup'
export FZF_DEFAULT_OPTS='--multi --extended'

#{%@@ if "work" in profile +@@%}
export JAVA_HOME="/opt/homebrew/opt/openjdk"

## Android Studio
# TODO: change path to actual android home
export ANDROID_HOME="$HOME/Library/Android/sdk"

## Appium
# https://appium.io/docs/en/2.1/cli/env-vars

# This is where drivers and plugins are installed
# By default, it will create a '.appium' dir in '~'
# export APPIUM_HOME="$XDG_DATA_HOME/appium"

# Use system 'unzip' binary instead of JS lib.
# If 'unzip' fails, it will use the lib as fallback though.
export APPIUM_PREFER_SYSTEM_UNZIP='1'
#{%@@ endif +@@%}

## ENV SETTINGS

# export SUDO_ASKPASS="$HOME/.local/bin/dmenupass"

[ ! -f "$XDG_CONFIG_HOME/shell/shortcuts.sh" ] && user_shortcuts

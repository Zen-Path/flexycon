#!/usr/bin/env sh

# {{@@ header() @@}}

# shellcheck disable=SC2139
#   Keep env vars in single quotes, so they are expanded when they're used,
#   not when they're defined.

# Make some system commands not require sudo.
for command in mount umount su shutdown reboot; do
    alias "$command"="sudo $command"
done
unset command

# Abbreviations
alias e='$EDITOR'
alias E='$VISUAL' # visual Editor
alias g='git'
alias t='task'
alias ka='killall'
alias sql='sqlite3'

# {%@@- if os == "linux" +@@%}
alias p='pacman'
# {%@@- endif +@@%}

# {%@@- if os == "linux" +@@%}
alias o='xdg-open'
# {%@@- elif os == "darwin" +@@%}
alias o='open'
# {%@@- endif +@@%}

# {%@@- if os == "linux" +@@%}
alias z='zathura'
# {%@@- endif +@@%}

# Verbosity and common settings.
alias cp='cp -iv'
alias mv='mv -iv'
alias rm='rm -vI'
alias bc='bc -ql'
alias rg='rg -i'
alias tp='trash-put --'
alias rsync='rsync -vrPlu'
alias mkd='mkdir -pv'
alias ffmpeg='ffmpeg -hide_banner'
alias shfmt='shfmt --indent 4 --binary-next-line --case-indent --space-redirects --write'

# {%@@- if os == "darwin" +@@%}
alias ls='ls -A -h --color=auto'
# {%@@- elif os == "linux" +@@%}
alias ls='ls --almost-all --human-readable --color=auto --group-directories-first'
# {%@@- elif os == "windows" +@@%}
alias ls='ls --almost-all --human-readable --color=auto --group-directories-first --classify'
# {%@@- endif +@@%}

# Use colored output
alias grep='grep --color=auto'
alias diff='diff --color=auto'
alias ip='ip -color=auto'

# Dev-oriented
alias mci='sudo make clean install'
alias tse='tsc --target es6'
alias jq='jq --indent 4'
alias jqs='jq --sort-keys'
alias adbpac='adb shell cmd package list packages'

## Python
alias py='python3'

# {%@@- if os == "darwin" +@@%}
# PYthon Brew
alias pyb='/opt/homebrew/bin/python3'
# {%@@- endif +@@%}

# Python ENVironment Create
# {%@@- if os == "linux" +@@%}
alias penvc='py -m venv venv'
# {%@@- elif os == "darwin" +@@%}
alias penvc='pyb -m venv venv'
# {%@@- endif +@@%}

# Python ENVironment Deactivate
alias penvd='deactivate && echo "Deactivated python environment."'

# Pip Freeze to Requirements
alias pfr='pip freeze | grep -v "^-e" > requirements.txt'

# Pip Install from Requirements
alias pir='pip install -r requirements.txt'

# Rclone
alias rc='rclone'
alias rcw='rclone_wrapper'

# YouTube
alias yt='yt-dlp'
alias ytt='yt --skip-download --write-thumbnail'
alias yts='mpv --slang=en --fs --ytdl-raw-options=ignore-config=,sub-lang=en,write-auto-sub='
alias yta='yt --extract-audio --format bestaudio/best'
alias ytap='yt --extract-audio --format bestaudio/best --yes-playlist -o "%(playlist_index)02d - %(title)s [%(id)s].%(ext)s"'

# General

# File Manager
# alias fm='$FILE_MANAGER'

# Package Manager
# {%@@- if os == "linux" +@@%}
# {%@@- if "arch" in distro_like +@@%}
alias pm='yay'
# {%@@- endif +@@%}
# {%@@- elif os == "darwin" +@@%}
alias pm='brew'
# {%@@- endif +@@%}

# {%@@- if "home" in profile +@@%}
alias je='journal_entry'
# {%@@- endif +@@%}

alias gld='gallery-dl'

alias tess='tesseract --oem 3 --psm 6 -l eng'

alias dot='dotdrop'
alias doti='dotdrop install'
# TODO: Remove once config is unified
# {%@@- if os == "windows" +@@%}
alias dotiw='dotdrop install --cfg config-windows.yaml'
# {%@@- endif +@@%}
alias dotc='dotdrop compare'

alias pc='pre-commit'
alias pcr='pre-commit run'
alias pcra='pre-commit run --all-files'

alias ushort='user_shortcuts'

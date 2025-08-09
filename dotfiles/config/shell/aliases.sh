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
alias E='$GRAPHICAL_EDITOR'
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

# {%@@- if os == "linux" +@@%}
alias ls='ls --almost-all --human-readable --color=auto --group-directories-first'
# {%@@- elif os == "darwin" +@@%}
alias ls='ls -A -h --color=auto'
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
# [Py]thon [B]rew
alias pyb='/opt/homebrew/bin/python3'
# {%@@- endif +@@%}

# [Python] Virtual [Env]ironment [C]reate
# {%@@- if os == "linux" +@@%}
alias penvc='py -m venv venv'
# {%@@- elif os == "darwin" +@@%}
alias penvc='pyb -m venv venv'
# {%@@- endif +@@%}

# [Python] Virtual [Env]ironment [D]eactivate
alias penvd='deactivate && echo "Deactivated python environment."'

# [P]ip [F]reeze to [R]equirements
alias pfr='pip freeze | grep -v "^-e" > requirements.txt'

# [P]ip [I]nstall from [R]equirements
alias pir='pip install -r requirements.txt'

# Rclone
alias rc='rclone'
alias rcfmt='rclone_fmt'
alias rc_c='rclone copy --progress --create-empty-src-dirs --exclude "No_Backup/**" --exclude ".git/"'
alias rc_cd='rc_c --dry-run'
alias rc_s='rclone sync --progress --create-empty-src-dirs --track-renames --exclude "No_Backup/**" --exclude ".git/"'
alias rc_sd='rc_s --dry-run'

# Taskwarrior
# TODO: use a similar approach to 'open_journal_entry' instead of
# only 'yesterday' and 'today'.
alias t-done-y='task end.after:yesterday end.before:today completed'
alias t-done-t='task end.after:today completed'

# YouTube
alias yt='yt-dlp'
alias ytt='yt --skip-download --write-thumbnail'
alias yts='mpv --slang=en --fs --ytdl-raw-options=ignore-config=,sub-lang=en,write-auto-sub='
alias yta='yt --extract-audio --format bestaudio/best'
alias ytap='yt --extract-audio --format bestaudio/best --yes-playlist -o "%(playlist_index)02d - %(title)s [%(id)s].%(ext)s"'

# General

# [F]ile [M]anager
# alias fm='$FILE_MANAGER'

# [P]ackage [M]anager
# {%@@- if os == "linux" +@@%}
# {%@@- if "arch" in distro_like +@@%}
alias pm='yay'
# {%@@- endif +@@%}
# {%@@- elif os == "darwin" +@@%}
alias pm='brew'
# {%@@- endif +@@%}

# {%@@- if "home" in profile +@@%}
# [J]ournal [E]ntry
alias je='journal_entry'
# {%@@- endif +@@%}

# [G]allery [D]ownload
alias gld='gallery-dl'

alias tess='tesseract --oem 3 --psm 6 -l eng'

alias dot='dotdrop'
alias doti='dotdrop install'

alias pc='pre-commit'
alias pcr='pre-commit run'
alias pcra='pre-commit run --all-files'

alias ushort='user_shortcuts'

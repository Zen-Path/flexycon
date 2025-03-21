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
HISTFILE="${XDG_CACHE_HOME:-$HOME/.cache}/zsh/history"
setopt appendhistory

# Load aliases and shortcuts if existent.
[ -f "${XDG_CONFIG_HOME:-$HOME/.config}/shell/shortcutrc" ] && source "${XDG_CONFIG_HOME:-$HOME/.config}/shell/shortcutrc"
[ -f "${XDG_CONFIG_HOME:-$HOME/.config}/shell/aliasrc" ] && source "${XDG_CONFIG_HOME:-$HOME/.config}/shell/aliasrc"
[ -f "${XDG_CONFIG_HOME:-$HOME/.config}/shell/zshnameddirrc" ] && source "${XDG_CONFIG_HOME:-$HOME/.config}/shell/zshnameddirrc"

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

function src_short() {
    shortcuts > /dev/null
    source ${XDG_CONFIG_HOME:-$HOME/.config}/shell/shortcutrc
    source ${XDG_CONFIG_HOME:-$HOME/.config}/shell/zshnameddirrc
    echo "Sourced shell shortcuts."
}

# Run a command on every 'Enter' (e.g. `run_loop cargo run`)
function run_loop {
    local cmd="$@"
    while true; do
        eval "$cmd"
        read
    done
}

function split_filename_extension() {
    full_filename=$1
    filename="${full_filename%.*}"
    extension="${full_filename##*.}"

    echo "$filename" "$extension"
}

function construct_output_path() {
    input_path=$1
    suffix=$2
    set -- $(split_filename_extension "$input_path")
    filename=$1
    extension=$2
    output_path="${filename}-${suffix}.${extension}"

    echo "$output_path"
}

function vidtoaudio() {
    input_path=$1
    output_path=$(construct_output_path "$input_path" "audio")

    ffmpeg -i "$input_path" -q:a 0 -map a "$output_path"
}

function vidopt() {
    input_path="$1"
    new_filename="$2"

    # Extract the root name and extension from the input path
    filename=$(basename -- "$input_path")
    root_name="${filename%.*}"
    extension="${filename##*.}"

    # Determine the output name
    if [ -z "$new_filename" ]; then
        output_name="${root_name}_compressed.${extension}"
    else
        output_name="$new_filename"
    fi

    ffmpeg -i "$input_path" -vcodec libx264 -crf 28 "$output_name"
}

function imgopt() {
    input_path=$1
    set -- $(split_filename_extension "$input_path")
    extension=$2
    output_path=$(construct_output_path "$input_path" "compressed")

    case "$extension" in
        jpg | jpeg)
            ffmpeg -i "$input_path" -q:v 10 "$output_path"
            ;;
        png)
            ffmpeg -i "$input_path" -compression_level 9 "$output_path"
            ;;
        *)
            echo "Unsupported image format: $extension"
            return 1
            ;;
    esac
}

function pdfopt() {
    input_path=$1
    output_path=$(construct_output_path "$input_path" "compressed")

    gs \
        -sDEVICE=pdfwrite \
        -dCompatibilityLevel=1.4 \
        -dDownsampleColorImages=true \
        -dColorImageResolution=150 \
        -dNOPAUSE \
        -dBATCH \
        -sOutputFile="$output_path" \
        "$input_path"
}

function trim_media() {
    if [ $# -ne 3 ]; then
        echo "Usage: trim_media input_file start_time duration"
        echo "Example: trim_media input.mp4 00:01:30 00:00:30"
        return 1
    fi

    local input_file=$1
    local start_time=$2
    local duration=$3
    local output_file="trimmed_${input_file%.*}.${input_file##*.}"

    ffmpeg -i "$input_file" -ss "$start_time" -t "$duration" -c copy "$output_file"

    echo "Trimmed file saved as $output_file"
}

function pdftopng() {
    magick -density 300 "$1" -quality 100 -alpha remove "$2"
}

function fm() {
    local tmp="$(mktemp -t "yazi-cwd.XXXXXX")" cwd
    yazi "$@" --cwd-file="$tmp"
    if cwd="$(command cat -- "$tmp")" && [ -n "$cwd" ] && [ "$cwd" != "$PWD" ]; then
        builtin cd -- "$cwd"
    fi
    command rm --force -- "$tmp"
}

function find_by_md5() {
    if [[ -z "$1" ]]; then
        echo "Usage: find_by_md5 <md5_hash>"
        return 1
    fi

    local target_hash="$1"

    fd -t f . | while IFS= read -r file; do
        hash=$(md5sum "$file" | awk '{print $1}')
        [[ "$hash" == "$target_hash" ]] && echo "$file"
    done
}

bindkey -s '^f' 'fzfopen\n'

# Set up fzf key bindings and fuzzy completion
if command -v fzf > /dev/null 2>&1; then
    source <(fzf --zsh)
fi

if command -v starship > /dev/null 2>&1; then
    eval "$(starship init zsh)"
fi

# Load syntax highlighting; should be last.
{%@@ if os == "darwin" @@%}
source $(brew --prefix)/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
{%@@ else @@%}
source /usr/share/zsh/plugins/fast-syntax-highlighting/fast-syntax-highlighting.plugin.zsh 2> /dev/null
{%@@ endif -@@%}

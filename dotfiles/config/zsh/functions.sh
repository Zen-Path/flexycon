#!/usr/bin/env zsh

# NOTE: Keep the main file content AFTER this line for templating purposes!

# Run a command on every 'Enter' (e.g. `run_loop cargo run`)
function run_loop() {
    while true; do
        "$@"
        print -n "\n:: Press Enter to rerun... "
        read < /dev/tty
    done
}

function split_filename_extension() {
    full_filename=$1
    filename="${full_filename%.*}"
    extension="${full_filename##*.}"

    echo "$filename" "$extension"
}

function fm() {
    local tmp="$(mktemp -t "yazi-cwd.XXXXXX")" cwd
    yazi "$@" --cwd-file="$tmp"
    if cwd="$(command cat -- "$tmp")" && [ -n "$cwd" ] && [ "$cwd" != "$PWD" ]; then
        builtin cd -- "$cwd"
    fi

    command rm -f -- "$tmp"
}

# Open a file or directory using fzf.
function fzfopen() {
    target_path="$(fzf --preview '\
    mime_type=$(file --mime-type -b {});\
    \
    case "$mime_type" in \
        inode/directory) \
            {%@@ if os == "darwin" @@%}
            ls -A -h --color=always {} \
            {%@@ elif os == "linux" @@%}
            ls -A -hN --color=always --group-directories-first {} ;; \
            {%@@ endif @@%}
            ;; \
        text/*) \
            bat --color=always --style=numbers --line-range=:50 {} 2> /dev/null ;; \
        *) \
            true ;; \
    esac')"

    [ -z "$target_path" ] && echo "No file was selected." && return 1

    echo "$target_path"

    fm "$target_path"
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

# DEVELOPMENT

# Python ENVironment Activate
function penva() {
    if [[ ! -z "$VIRTUAL_ENV" ]]; then
        echo "Virtual env is already active; found at '$VIRTUAL_ENV'."
        return 0
    fi

    local env_dirs=("venv" ".venv" "env")
    local activate_script=""
    local dir="${1:-$PWD}"

    while :; do
        for env in "${env_dirs[@]}"; do
            local candidate="$dir/$env/bin/activate"
            if [[ -f "$candidate" ]]; then
                activate_script="$candidate"
                break 2 # Exit both loops
            fi
        done

        # Stop at root or $HOME
        [[ "$dir" == "$HOME" || "$dir" == "/" ]] && break
        dir="$(dirname "$dir")"
    done

    if [[ -z "$activate_script" ]]; then
        echo "Error: No virtual env activation script found from '$(pwd)' upwards to \$HOME." >&2
        return 1
    fi

    source "$activate_script"
    printf "Virtual environment activated; found at '%s'.\n" "$activate_script"
}

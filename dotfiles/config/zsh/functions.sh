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

function webmp_to_mp4() {
    local input_path="$1"
    set -- $(split_filename_extension "$input_path")
    filename=$1

    ffmpeg -fflags +genpts -i "$input_path" -r 24 "$filename.mp4"
}

function vid_rotate() {
    local input_path="$1"
    local output_path=$(construct_output_path "$input_path" "rotated")

    ffmpeg -i "$input_path" -vf "transpose=1" "$output_path"
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

    [ -z "$target_path" ] && exit 1

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
        echo "Error: no virtualenv activate script found from '$(pwd)' upwards to '$HOME'" >&2
        return 1
    fi

    source "$activate_script"
    printf "➜ Activated %s\n" "$activate_script"
}

#!/bin/sh

# Open a file or directory using fzf.

target_path="$(fzf --preview '\
mime_type=$(file --mime-type -b {});\
\
case "$mime_type" in \
    inode/directory) \
        ls -A -hN --color=always --group-directories-first {} ;; \
    text/*) \
        bat --color=always --style=numbers --line-range=:50 {} 2> /dev/null ;; \
    *) \
        true ;; \
esac')"

[ -z "$target_path" ] && exit 1

"$FILE_MANAGER" "$target_path"

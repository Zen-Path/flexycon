#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -lt 3 ]; then
    echo "Usage: $0 <in_format> <out_format> <files...>"
    exit 1
fi

in_format=$1
out_format=$2

echo ":: Converting files from '$in_format' to '$out_format'."

# Shift the arguments to access the file list
shift 2

counter=1
for file in "$@"; do
    if [[ "$file" == *.$in_format ]]; then
        output_file="${file%.$in_format}.$out_format"
        magick "$file" -define png:compression-level=9 "$output_file"
        echo "$counter. Converted '$file' to '$output_file'."
        counter=$((counter + 1))
    else
        echo "Skipping '$file': does not match input format '$in_format'."
    fi
done

echo ":: Conversion completed."

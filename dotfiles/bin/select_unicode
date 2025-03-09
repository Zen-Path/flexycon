#!/bin/bash

# Promt the user for a unicode character and copies or inserts it.

UNICODE_DIR="$XDG_DATA_HOME/unicode"
# List of files containing unicode characters
FILES="icons math alphanum flags braille"

prompt(){ dmenu -p "Select char" -l 30 ;}

# Prompt user for a file or an emoji
char="$(printf "%s\n" $FILES "$(cat $UNICODE_DIR/emoji)" | prompt)"

# If selection is a file, prompt the user again
[ -f "$UNICODE_DIR/$char" ] && char="$(cat "$UNICODE_DIR/$char" | prompt)"

# Quit if empty selection
[ -z "$char" ] && exit

# Discard the name of the character
char="$(echo $char | sed "s/ .*//")"

# Running the script with an argument automatically inserts the selected
# character. Otherwise, the character is copied and a the user notified.
if [ -n "$1" ]; then
	xdotool type "$char"
else
	printf "%s" "$char" | xclip -selection clipboard
	notify-send "'$char' was copied."
fi

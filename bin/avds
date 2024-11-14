#!/bin/sh

selected_avd="$(emulator -list-avds | grep -v "^INFO" | dmenu -i -l -1 -p "Select emulator")"

[ -z "$selected_avd" ] && exit

emulator -avd "$selected_avd"

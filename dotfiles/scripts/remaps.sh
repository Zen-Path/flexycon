#!/bin/sh

# This script is called on startup to remap keys.
# Set key repeat delay and key repeat rate (n / second).
xset r rate 325 40
# Map the caps lock key to super, and map the menu key to right super.
setxkbmap -option caps:super,altwin:menu_win
# When caps lock is pressed only once, treat it as escape
killall xcape 2> /dev/null
xcape -e 'Super_L=Escape'
# Turn off caps lock if on since there is no longer a key for it.
xset -q | grep -q "Caps Lock:\s*on" && xdotool key Caps_Lock

xmodmap -e "keycode 9 = Escape asciitilde"

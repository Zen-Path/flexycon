#!/bin/sh

# Show wifi 📶 and percent strength or 📡 if none.
# Show 🌐 if connected to ethernet or ❎ if none.
# Show 🔒 if a vpn connection is active

toggle_wifi() {
    status="$(nmcli radio wifi)"
    if [[ "$status" = "disabled" ]]; then
        nmcli radio wifi on
    else
        nmcli radio wifi off
    fi
}

case $BLOCK_BUTTON in
    1) "$TERMINAL" -e nmtui ;;
    2) toggle_wifi ;;
    3) notify-send "🌐 Internet module" -- "\
Show internet status.

<b>Actions</b>
- Left   : Open nmtui
- Middle : Toggle wifi
- Right  : Show this message

<b>Status</b>
- 🌐: ethernet working
- ❎: no ethernet
- 📶: wifi connection with quality
- 📡: no wifi connection
- ❌: wifi disabled
- 🔒: vpn is active
" ;;
    8) setsid -f "$TERMINAL" -e "$EDITOR" "$0" ;;
esac

# Wifi
wifiicon=""
if [ "$(cat /sys/class/net/w*/operstate 2> /dev/null)" = 'up' ]; then
    wifiicon="$(awk '/^\s*w/ { print "📶", int($3 * 100 / 70) "% " }' /proc/net/wireless)"
elif [ "$(cat /sys/class/net/w*/operstate 2> /dev/null)" = 'down' ]; then
    [ "$(cat /sys/class/net/w*/flags 2> /dev/null)" = '0x1003' ] && wifiicon="📡 " || wifiicon="❌ "
fi

# Ethernet
[ "$(cat /sys/class/net/e*/operstate 2> /dev/null)" = 'up' ] && ethericon="🌐" || ethericon="❎"

# TUN
tunicon=""
[ -n "$(cat /sys/class/net/tun*/operstate 2> /dev/null)" ] && tunicon=" 🔒"

printf "%s%s%s\n" "$wifiicon" "$ethericon" "$tunicon"

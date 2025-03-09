#!/bin/sh

# A dmenu wrapper script for system functions.

export WM="dwm"
case "$(readlink -f /sbin/init)" in
	*systemd*) ctl='systemctl' ;;
	*) ctl='loginctl' ;;
esac

wmpid(){ # This function is needed if there are multiple instances of the window manager.
	tree="$(pstree -ps $$)"
	tree="${tree#*$WM(}"
	echo "${tree%%)*}"
}

wait_display () {
	while [ "$(xset q | tail -1)" != "  Monitor is On" ]; do
    	sleep 15
	done
}

pause_dunst(){
	# https://wiki.archlinux.org/title/Dunst
	dunstctl set-paused true
	time1=$(date '+%s')

	eval "$1"
	wait_display

	time2=$(date '+%s')
	delta=$((time2 - time1))
	fmt_delta="$(date -u -d @${delta} '+%Hh %Mm %Ss')"

	dunstctl set-paused false
	notify-send --urgency low "Welcome back!" "You've been gone for $fmt_delta."
}

choices="\
sleep 😴
lock 🔒
power off 🔌
reboot 🔄
exit $WM 🚪
update $WM 
display off 📺
hibernate 🐻
"

choice="$(printf "%s" "$choices" | dmenu -i -l -1 -p "Action")"

case "$choice" in
	'sleep 😴') pause_dunst "slock $ctl suspend -i" ;;
	'lock 🔒') pause_dunst 'slock' ;;
	'power off 🔌') $ctl poweroff -i ;;
	'reboot 🔄') $ctl reboot -i ;;
	"exit $WM 🚪") kill -TERM "$(wmpid)" ;;
	"update $WM ") echo "wmpid: $(wmpid)"; kill -HUP "$(wmpid)" ;;
	'display off 📺') xset dpms force off ;;
	'hibernate 🐻') pause_dunst "slock $ctl hibernate -i" ;;
	*) exit 1 ;;
esac

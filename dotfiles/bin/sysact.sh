#!/bin/sh

# A dmenu wrapper script for system functions.

export WM="dwm"
case "$(readlink -f /sbin/init)" in
    *systemd*) ctl='systemctl' ;;
    *) ctl='loginctl' ;;
esac

wmpid() { # This function is needed if there are multiple instances of the window manager.
    tree="$(pstree -ps $$)"
    tree="${tree#*$WM(}"
    echo "${tree%%)*}"
}

wait_display() {
    while [ "$(xset q | tail -1)" != "  Monitor is On" ]; do
        sleep 15
    done
}

power_manager() {
    # $1: The power action (suspend, hibernate, lock)

    # https://wiki.archlinux.org/title/Dunst
    dunstctl set-paused true
    time1=$(date '+%s')

    # Before locking the screen, turn off caps lock just in case
    xset q | grep -q "Caps Lock:   on" && xdotool key Caps_Lock

    slock &
    SLOCK_PID=$!

    sleep 1

    if [ "$1" = "suspend" ] || [ "$1" = "hibernate" ]; then
        $ctl "$1" -i

        # Path B: Ghost-wake prevention
        (
            sleep 45
            if ps -p $SLOCK_PID > /dev/null; then
                power_manager "$1"
            fi
        ) &
        WATCHER_PID=$!
    fi

    # Path A: Wait for the user to manually unlock slock
    wait $SLOCK_PID

    # Once unlocked, we immediately kill Path B
    [ -n "$WATCHER_PID" ] && kill "$WATCHER_PID" 2> /dev/null

    time2=$(date '+%s')
    delta=$((time2 - time1))
    fmt_delta="$(date -u -d @${delta} '+%Hh %Mm %Ss')"

    dunstctl set-paused false
    notify-send --urgency low "Welcome back!" "You've been gone for $fmt_delta."
}

choices="\
😴 sleep
🔒 lock
🔌 power off
🔄 reboot
🚪 exit $WM
 update $WM
📺 display off
🐻 hibernate
"

choice="$(printf "%s" "$choices" | dmenu -i -l -1 -p "Action")"

case "$choice" in
    '😴 sleep') power_manager 'suspend' ;;
    '🔒 lock') power_manager 'lock' ;;
    '🔌 power off') $ctl poweroff -i ;;
    '🔄 reboot') $ctl reboot -i ;;
    "🚪 exit $WM") kill -TERM "$(wmpid)" ;;
    " update $WM")
        echo "wmpid: $(wmpid)"
        kill -HUP "$(wmpid)"
        ;;
    '📺 display off') xset dpms force off ;;
    '🐻 hibernate') power_manager 'hibernate' ;;
    *) exit 1 ;;
esac

#!/bin/sh

show_calendar() {
    local current_day=$(date +%-d)
    notify-send "Calendar" "$(cal | sed -E "s/\b$current_day\b/<span color='#1D2021'><b>&<\/b><\/span>/")"
}

show_appointments() {
    if command -v calcurse > /dev/null; then
        local appointments="$(calcurse -d3)"
        if [ -n "$appointments" ]; then
            notify-send "Appointments" "$appointments"
        else
            notify-send "Appointments" "No upcoming appointments."
        fi
    else
        # notify-send "Error" "calcurse is not installed."
        true
    fi
}

case $BLOCK_BUTTON in
    1)
        show_calendar
        show_appointments
        ;;
    2)
        if command -v calcurse > /dev/null; then
            setsid -f "$TERMINAL" -e calcurse
        else
            # notify-send "Error" "calcurse is not installed."
            true
        fi
        ;;
    3)
        notify-send "📅 Date module" -- "\
Show the current date and time.

<b>Actions</b>
- Left   : Show calendar and upcoming appointments
- Middle : Open calcurse
- Right  : Show this message"
        ;;
    8)
        "$TERMINAL" -e "$EDITOR" "$0"
        ;;
esac

date '+%d %b (%a) %H:%M'

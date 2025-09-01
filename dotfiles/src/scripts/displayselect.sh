#!/bin/sh

# A UI for detecting and selecting all displays. Probes xrandr for connected
# displays and lets user select one to use. User may also select "manual
# selection" which opens arandr.

# If multi-monitor is selected and there are two screens.
two_screen() {
    mirror=$(printf "no\\nyes" | dmenu -i -p "Mirror displays?")
    # Mirror displays using native resolution of external display and a scaled
    # version for the internal display
    if [ "$mirror" = "yes" ]; then
        external=$(echo "$screens" | dmenu -i -p "Optimize resolution for:")
        internal=$(echo "$screens" | grep -v "$external")

        res_external=$(xrandr --query | sed -n "/^$external/,/\+/p" \
            | tail -n 1 | awk '{print $1}')
        res_internal=$(xrandr --query | sed -n "/^$internal/,/\+/p" \
            | tail -n 1 | awk '{print $1}')

        res_ext_x=$(echo "$res_external" | sed 's/x.*//')
        res_ext_y=$(echo "$res_external" | sed 's/.*x//')
        res_int_x=$(echo "$res_internal" | sed 's/x.*//')
        res_int_y=$(echo "$res_internal" | sed 's/.*x//')

        scale_x=$(echo "$res_ext_x / $res_int_x" | bc -l)
        scale_y=$(echo "$res_ext_y / $res_int_y" | bc -l)

        xrandr --output "$external" --auto --scale 1.0x1.0 \
            --output "$internal" --auto --same-as "$external" \
            --scale "$scale_x"x"$scale_y"
    else

        primary=$(echo "$screens" | dmenu -i -p "Select primary display:")
        secondary=$(echo "$screens" | grep -v ^"$primary"$)
        direction=$(printf "left\\nright" | dmenu -i -p "What side of $primary should $secondary be on?")
        xrandr --output "$primary" --auto --scale 1.0x1.0 --output "$secondary" --"$direction"-of "$primary" --auto --scale 1.0x1.0
    fi
}

# If multi-monitor is selected and there are more than two screens.
more_screen() {
    primary=$(echo "$screens" | dmenu -i -p "Select primary display:")
    secondary=$(echo "$screens" | grep -v ^"$primary"$ | dmenu -i -p "Select secondary display:")
    direction=$(printf "left\\nright" | dmenu -i -p "What side of $primary should $secondary be on?")
    tertiary=$(echo "$screens" | grep -v ^"$primary"$ | grep -v ^"$secondary"$ | dmenu -i -p "Select third display:")
    xrandr --output "$primary" --auto --output "$secondary" --"$direction"-of "$primary" --auto --output "$tertiary" --"$(printf "left\\nright" | grep -v "$direction")"-of "$primary" --auto
}

# Multi-monitor handler.
multi_monitor() {
    case "$(echo "$screens" | wc -l)" in
        2) two_screen ;;
        *) more_screen ;;
    esac
}

# If only one output available or chosen.
one_screen() {
    xrandr --output "$1" --auto --scale 1.0x1.0 $(echo "$all_possible" | grep -v "\b$1" | awk '{print "--output", $1, "--off"}' | paste -sd ' ' -)
}

# Stuff to run to clean up.
post_run() {
    setbg # Fix background if screen size/arrangement has changed.
    {
        killall dunst
        setsid -f dunst
    } > /dev/null 2>&1 # Restart dunst to ensure proper location on screen
}

# Get all possible displays
all_possible=$(xrandr -q | grep "connected")

# Get all connected screens.
screens=$(echo "$all_possible" | awk '/ connected/ {print $1}')

# If there's only one screen
[ "$(echo "$screens" | wc -l)" -lt 2 ] \
    && {
        one_screen "$screens"
        post_run
        notify-send "💻 Only one screen detected." "Using it in its optimal settings..."
        exit
    }

# Get user choice including multi-monitor and manual selection:
chosen=$(printf "%s\\nmulti-monitor\\nmanual selection" "$screens" | dmenu -i -p "Select display arrangement:") \
    && case "$chosen" in
        "manual selection")
            arandr
            exit
            ;;
        "multi-monitor") multi_monitor ;;
        *) one_screen "$chosen" ;;
    esac

post_run

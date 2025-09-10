#!/bin/sh

# Usage:
# `$0`: Ask for recording type via dmenu
# `$0 screencast`: Record both audio and screen
# `$0 video`: Record only screen
# `$0 audio`: Record only audio
# `$0 kill`: Kill existing recording
#
# If there is already a running instance, user will be prompted to end it.

videos_dir="$HOME/Videos/Screencasts"
audio_dir="$HOME/Music"
date_fmt='%Y-%m-%d_%H-%M-%S'

[ ! -d "$videos_dir" ] && mkdir -p "$videos_dir"
[ ! -d "$audio_dir" ] && mkdir -p "$audio_dir"

# Utils

get_dimensions() { xrandr | grep -oP '(?<=current ).*(?=,)' | tr -d ' '; }

update_icon() {
    echo "$1" > /tmp/recording_icon
    pkill -RTMIN+9 "${STATUSBAR:-dwmblocks}"
}

kill_recording() {
    recpid="$(cat /tmp/recording_pid)"
    kill -15 "$recpid"
    rm -f /tmp/recording_pid
}

get_selection() {
    slop \
        --bordersize 4.0 \
        --padding 0.0 \
        --tolerance 20.0 \
        --color=100.0,0.0,0.0,0.3 \
        --nodrag \
        --highlight \
        --nodecorations=2 \
        --format "%x %y %w %h" \
        --quiet
}

# Recording Modes
# TODO - unify both video_selected function so there's no duplication
video_selected_hidef() {
    # POSIX-compliant.
    set -- $(get_selection)
    [ -z "$1" ] \
        && notify-send "Recording cancelled" "Recording was cancelled by keystroke or right-click." \
        && exit 1

    X=$1
    Y=$2
    W=$3
    H=$4

    output_path="$videos_dir/box-$(date "+$date_fmt").mp4"

    ffmpeg \
        -f x11grab \
        -framerate 25 \
        -video_size "$W"x"$H" \
        -i :0.0+"$X,$Y" \
        -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
        -c:v libx265 \
        -qp 0 -r 30 \
        -pix_fmt yuv420p \
        "$output_path" &

    echo "$output_path" > /tmp/recording_path
    echo $! > /tmp/recording_pid
    update_icon "⏺️"
}

video_selected() {
    # POSIX-compliant.
    set -- $(get_selection)
    [ -z "$1" ] \
        && notify-send "Recording cancelled" "Recording was cancelled by keystroke or right-click." \
        && exit 1

    X=$1
    Y=$2
    W=$3
    H=$4

    output_path="$videos_dir/box-$(date "+$date_fmt").mp4"

    ffmpeg \
        -f x11grab \
        -framerate 25 \
        -video_size "$W"x"$H" \
        -i :0.0+"$X,$Y" \
        -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
        -c:v libx264 \
        -pix_fmt yuv420p \
        "$output_path" &

    echo "$output_path" > /tmp/recording_path
    echo $! > /tmp/recording_pid
    update_icon "⏺️"
}

video() {
    ffmpeg \
        -f x11grab \
        -framerate 30 \
        -s "$(get_dimensions)" \
        -i "$DISPLAY" \
        -c:v libx264 -qp 0 -r 30 \
        "$HOME/video-$(date "+$date_fmt").mp4" &

    echo $! > /tmp/recording_pid
    update_icon "⏺️"
}

screencast() {
    ffmpeg -y \
        -f x11grab \
        -framerate 30 \
        -s "$(get_dimensions)" \
        -i "$DISPLAY" \
        -r 24 \
        -use_wallclock_as_timestamps 1 \
        -f alsa -thread_queue_size 1024 -i default \
        -c:v h264 \
        -crf 0 -preset ultrafast -c:a aac \
        "$HOME/screencast-$(date "+$date_fmt").mp4" &

    echo $! > /tmp/recording_pid
    update_icon "⏺️🎙️"
}

webcam_hidef() {
    ffmpeg \
        -f v4l2 \
        -i /dev/video0 \
        -video_size 1920x1080 \
        "$HOME/webcam-$(date "+$date_fmt").mp4" &

    echo $! > /tmp/recording_pid
    update_icon "🎥"
}

webcam() {
    ffmpeg \
        -f v4l2 \
        -i /dev/video0 \
        -video_size 640x480 \
        "$HOME/webcam-$(date "+$date_fmt").mp4" &

    echo $! > /tmp/recording_pid
    update_icon "🎥"
}

audio() {
    ffmpeg \
        -f alsa -i default \
        -c:a flac \
        "$HOME/audio-$(date "+$date_fmt").flac" &

    echo $! > /tmp/recording_pid
    update_icon "🎙️"
}

# Main

ask_recording() {
    choices="\
video selected
video selected (hi-def)
video
screencast
audio
webcam
webcam (hi-def)"

    choice=$(printf "%s\n" "$choices" | dmenu -l -1 -i -p "Recording mode")

    case "$choice" in
        screencast) screencast ;;
        audio) audio ;;
        video) video ;;
        "video selected") video_selected ;;
        "video selected (hi-def)") video_selected_hidef ;;
        webcam) webcam ;;
        "webcam (hi-def)") webcam_hidef ;;
    esac

    # dunstctl set-paused true
}

ask_to_end() {
    response=$(printf "Yes\\nNo" | dmenu -i -p "End active recording?") \
        && [ "$response" = "Yes" ] \
        && kill_recording
}

case "$1" in
    screencast) screencast ;;
    audio) audio ;;
    video) video ;;
    *selected) video_selected ;;
    kill) kill_recording ;;
    *)
        # Sleep to avoid the notification from appearing in the video
        # TODO: instead of unpausing, revert to the status that was active before
        # the recording
        ([ -f /tmp/recording_pid ] \
            && ask_to_end \
            && sleep 0.3 \
            && dunstctl set-paused false \
            && notify-send "Recording saved" "Recording was saved at '$(sed "s|$HOME|~|g" /tmp/recording_path)'." \
            && exit) || ask_recording
        ;;

esac

#!/bin/sh

STATE_DIR="${HOME}/.local/state/taskwarrior"
STATE_FILE="${STATE_DIR}/overdue_tasks"

# Create state directory if it doesn't exist
mkdir -p "$STATE_DIR"

# Notify user if more tasks have become overdue
notify_user() {
    new_overdue=$1
    old_overdue=$2
    difference=$((new_overdue - old_overdue))

    if [ "$difference" -gt 0 ]; then
        notify-send "Taskwarrior Alert" "$difference task(s) become overdue."
    fi
}

# Read previous overdue tasks count
if [ -f "$STATE_FILE" ]; then
    old_overdue=$(cat "$STATE_FILE")
else
    old_overdue=0
fi

# Get current task counts
pending_tasks=$(task +PENDING count)
overdue_tasks=$(task +OVERDUE count)
due_tasks=$((pending_tasks - overdue_tasks))

echo "$overdue_tasks" > "$STATE_FILE"

notify_user "$overdue_tasks" "$old_overdue"

# Handle button clicks
case "$BLOCK_BUTTON" in
    1) setsid -f "$TERMINAL" -e taskwarrior-tui ;;
    3) notify-send " Due and overdue tasks" "\- Left click to open 'taskwarrior-tui'" ;;
    8) "$TERMINAL" -e "$EDITOR" "$0" ;;
esac

# Output task information
if [ "$overdue_tasks" -ne 0 ]; then
    printf "%s %s\n" "$due_tasks" "$overdue_tasks"
else
    printf "%s\n" "$due_tasks"
fi

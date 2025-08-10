#!/usr/bin/env python3

import os
import subprocess
import sys

from scripts.statusbar.shared import EDITOR, STATUSBAR, TERMINAL, MouseButton


def handle_block_button(button_id):
    """Handle block button events."""
    match button_id:
        case MouseButton.LEFT.value:
            subprocess.Popen(["setsid", "-w", "-f", TERMINAL, "-e", "pulsemixer"])
            subprocess.run(["pkill", f"-RTMIN+10", STATUSBAR])
        case MouseButton.MIDDLE.value:
            subprocess.run(["wpctl", "set-mute", "@DEFAULT_SINK@", "toggle"])
        case MouseButton.RIGHT.value:
            subprocess.run(
                [
                    "notify-send",
                    "📢 Volume module",
                    "Show volume, 🔇 if muted.\n\n<b>Actions</b>\n- Middle click to mute\n- Scroll to change",
                ]
            )
        case MouseButton.EXTRA_1.value:
            subprocess.run(["wpctl", "set-volume", "@DEFAULT_SINK@", "1%+"])
        case MouseButton.EXTRA_2.value:
            subprocess.run(["wpctl", "set-volume", "@DEFAULT_SINK@", "1%-"])
        case MouseButton.EXTRA.value:
            subprocess.Popen([TERMINAL, "-e", EDITOR, __file__])


def main():
    block_button = os.environ.get("BLOCK_BUTTON")
    if block_button:
        handle_block_button(int(block_button))

    # Get volume info
    get_volume_result = subprocess.check_output(
        ["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"], text=True
    ).strip()

    # Extract numeric part after 'Volume: '
    volume_float = get_volume_result.replace("Volume: ", "").split()[0]
    volume_int = round(float(volume_float) * 100)

    # Choose icon
    if volume_int >= 70:
        icon = "🔊"
    elif volume_int >= 30:
        icon = "🔉"
    else:
        icon = "🔈"

    # Check mute status
    if "[MUTED]" in get_volume_result:
        icon = "🔇"

    print(f"{icon}{volume_int}%")


if __name__ == "__main__":
    main()

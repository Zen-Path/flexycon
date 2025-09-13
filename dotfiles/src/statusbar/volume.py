#!{{@@ env['FLEXYCON_HOME'] @@}}/venv/bin/python

import os
import subprocess
import sys

from common.helpers import notify, run_command
from common.logger import logger
from statusbar.shared import (
    EDITOR,
    STATUSBAR,
    TERMINAL,
    MouseButton,
    handle_block_button,
)


def update_volume(amount: int):
    run_command(
        [
            "wpctl",
            "set-volume",
            "@DEFAULT_SINK@",
            f"{abs(amount)}%{'-' if amount < 0 else '+'}",
        ]
    )


def toggle_mute():
    run_command(["wpctl", "set-mute", "@DEFAULT_SINK@", "toggle"])


ACTIONS = {
    MouseButton.LEFT: lambda: (
        run_command(["setsid", "-w", "-f", TERMINAL, "-e", "pulsemixer"]),
        run_command(["pkill", f"-RTMIN+10", STATUSBAR]),
    ),
    MouseButton.MIDDLE: toggle_mute,
    MouseButton.RIGHT: lambda: notify(
        "📢 Volume module",
        "Show sound volume, 🔇 if muted.\n"
        "\n<b>Actions</b>\n"
        "- Left click to open 'pulsemixer'\n"
        "- Middle click to mute\n"
        "- Right click to show this message\n"
        "- Scroll to update",
    ),
    MouseButton.SCROLL_UP: lambda: update_volume(2),
    MouseButton.SCROLL_DOWN: lambda: update_volume(-2),
    MouseButton.EXTRA_3: lambda: run_command([TERMINAL, "-e", EDITOR, __file__]),
}


def main():
    handle_block_button(ACTIONS)

    # Should return something like this:
    # - 'Volume: 0.55'
    # - 'Volume: 0.50 [MUTED]'
    volume_info = run_command(
        ["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"]
    ).output.strip()

    logger.debug(f"Volume info: {volume_info}")

    if volume_info.startswith("Could not connect to"):
        print("⛔ Connection")
        return

    volume_int = round(float(volume_info.split(" ")[1]) * 100)

    if "[MUTED]" in volume_info:
        icon = "🔇"
    else:
        if volume_int >= 70:
            icon = "🔊"
        elif volume_int >= 30:
            icon = "🔉"
        else:
            icon = "🔈"

    print(f"{icon}{volume_int}%")


if __name__ == "__main__":
    main()

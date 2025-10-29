#!/usr/bin/env python3

import argparse
import os
import subprocess
from datetime import datetime

from common.helpers import ensure_directories_exist
from common.packages.models import ClipboardUtility


class MaimUtility:
    def __init__(
        self,
        bordersize=4.0,
        padding=0.0,
        tolerance=20.0,
        color=(100.0, 0.0, 0.0, 0.3),
        nodecorations=2,
        hidecursor=True,
        quiet=True,
        delay=0.2,
        window=None,
    ):
        self.bordersize = bordersize
        self.padding = padding
        self.tolerance = tolerance
        self.color = color  # Expecting a tuple or list of floats
        self.nodecorations = nodecorations
        self.hidecursor = hidecursor
        self.quiet = quiet
        self.delay = delay
        self.window = window

    def _color_to_string(self):
        """Convert the color array to a string representation."""
        return ",".join(f"{c:.1f}" for c in self.color)

    def run(self, output_path, select=False):
        """Run maim with the configured options."""
        cmd = [
            "maim",
            f"--bordersize={self.bordersize}",
            f"--padding={self.padding}",
            f"--tolerance={self.tolerance}",
            f"--color={self._color_to_string()}",
            f"--nodecorations={self.nodecorations}",
        ]
        if self.hidecursor:
            cmd.append("--hidecursor")
        if self.quiet:
            cmd.append("--quiet")
        if self.window:
            cmd.extend(["--window", self.window, "--capturebackground"])

        if select:
            cmd.extend(["--select", "--nodrag", "--highlight"])

        cmd.extend(["--delay", str(self.delay)])
        cmd.append(output_path)

        ensure_directories_exist(output_path)

        result = subprocess.run(cmd)
        return result.returncode == 0


class ScreenshotUtility:
    def __init__(
        self,
        maim=None,
        clipboard=None,
        output_dir=None,
    ):
        self.maim = maim or MaimUtility()
        self.clipboard = clipboard or ClipboardUtility.get_instance()
        self.output_dir = os.path.expanduser(
            output_dir or f"{os.getenv("XDG_PICTURES_DIR", "~/Pictures")}/Screenshots"
        )

    def _capture(self, output_path, copy_output, select=False):
        response = self.maim.run(output_path, select)

        if response and copy_output:
            self.clipboard.file(output_path)

    def compose_output_path(self, capture_type, name=None, ext="png"):
        """Generate a file path to the output directory with the current timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        name_fmt = f"-{name[:100].replace(" ", "-")}" if name else ""

        return os.path.join(
            self.output_dir,
            f"{timestamp}_{capture_type}{name_fmt}.{ext}".lower(),
        )

    def area(self, copy_output=False):
        """Capture a selected area."""
        output_path = self.compose_output_path("area")
        self._capture(output_path, copy_output, select=True)

    def window(self, window=None, include_window_name=False, copy_output=False):
        """Capture a window."""
        # TODO: Implement a proper Window class

        if window is None:
            window = (
                subprocess.check_output(["xdotool", "getactivewindow"]).strip().decode()
            )

        window_name = None
        if include_window_name:
            window_name = (
                subprocess.check_output(["xdotool", "getwindowname", window])
                .strip()
                .decode()
            )

        output_path = self.compose_output_path("window", name=window_name)

        self.maim.window = window
        self._capture(output_path, copy_output)

    def screen(self, screen=None, copy_output=False):
        """Capture a screen."""
        # TODO: Implement logic
        self.full_screen(copy_output)

    def full_screen(self, copy_output=False):
        """Capture all screens."""
        output_path = self.compose_output_path("full")
        self._capture(output_path, copy_output)


def prompt_user(actions):
    options = list(actions.keys())

    choice = (
        subprocess.run(
            ["dmenu", "-i", "-l", "-1", "-p", "Screenshot"],
            input="\n".join(options).encode(),
            stdout=subprocess.PIPE,
        )
        .stdout.decode()
        .strip()
    )

    if choice in actions:
        actions[choice]()
    else:
        print("Invalid choice.")


def build_parser():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Screenshot Utility")

    # Create subparsers for actions
    subparsers = parser.add_subparsers(dest="action", help="Screenshot action")

    # Area action
    subparsers.add_parser("area", help="Capture a selected area")

    # Window action with additional options
    window_parser = subparsers.add_parser(
        "window", help="Capture the active or specified window"
    )
    window_parser.add_argument(
        "-w", "--window-id", type=str, help="Specify a window ID"
    )
    window_parser.add_argument(
        "-n",
        "--include-name",
        action="store_true",
        help="Include window name in the file name",
    )

    # Screen action with additional options
    screen_parser = subparsers.add_parser(
        "screen", help="Capture the screen where the active window resides"
    )
    screen_parser.add_argument(
        "-s", "--screen-name", type=str, help="Specify the screen name"
    )

    # Full action
    subparsers.add_parser("full", help="Capture all screens")

    # Global options
    copy_group = parser.add_mutually_exclusive_group()
    copy_group.add_argument(
        "--copy",
        dest="copy",
        action="store_true",
        default=True,
        help="Copy the screenshot to the clipboard (default)",
    )
    copy_group.add_argument(
        "--no-copy",
        dest="copy",
        action="store_false",
        help="Do not copy the screenshot to the clipboard",
    )

    parser.add_argument(
        "-d",
        "--output-directory",
        type=str,
        default=None,
        help="Set the output directory for screenshots",
    )

    return parser


def main():
    args = build_parser().parse_args()

    screenshot_utility = ScreenshotUtility(
        output_dir=args.output_directory if args.output_directory else None
    )

    if not args.action:
        actions = {
            "🔳 Area": lambda: screenshot_utility.area(copy_output=args.copy),
            "🪟 Window": lambda: screenshot_utility.window(copy_output=args.copy),
            "🖥️ Screen": lambda: screenshot_utility.screen(copy_output=args.copy),
            "🌍 Full Screen": lambda: screenshot_utility.full_screen(
                copy_output=args.copy
            ),
        }
        prompt_user(actions)
        return

    match args.action:
        case "area":
            screenshot_utility.area(copy_output=args.copy)
        case "window":
            screenshot_utility.window(
                window=args.window_id,
                include_window_name=args.include_name,
                copy_output=args.copy,
            )
        case "screen":
            screenshot_utility.screen(screen=args.screen_name, copy_output=args.copy)
        case "full":
            screenshot_utility.full(copy_output=args.copy)
        case _:
            raise ValueError(f"Unknown action: {args.action}")


if __name__ == "__main__":
    main()

#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging

from common.cmd_utilities import run_cmd_background
from common.helpers import NotificationSystem, get_version
from common.logger import log, setup_logging
from common.statusbar import (
    EDITOR,
    TERMINAL,
    MouseButton,
    handle_block_button,
)
from statusbar.network.src.core import (
    get_ethernet_info,
    get_vpn_info,
    get_wifi_info,
    toggle_wifi,
)

ACTIONS = {
    MouseButton.LEFT: lambda: run_cmd_background([TERMINAL, "-e", "nmtui"]),
    MouseButton.MIDDLE: toggle_wifi,
    MouseButton.RIGHT: lambda: NotificationSystem.run(
        "🌐 Network",
        "Show network status.\n"
        "\n<b>Actions</b>\n"
        "- Left   : Open nmtui\n"
        "- Middle : Toggle wifi\n"
        "- Right  : Show this message\n"
        "- Extra  : Edit this script"
        "\n<b>Status</b>\n"
        "- 🌐: ethernet working\n"
        "- ❎: no ethernet\n"
        "- 📶: wifi connection with quality\n"
        "- 📡: no wifi connection\n"
        "- ❌: wifi disabled\n"
        "- 🔒: vpn is active",
    ),
    MouseButton.EXTRA_3: lambda: run_cmd_background(
        [TERMINAL, "-e", EDITOR, "{{@@ _dotfile_abs_src @@}}"]
    ),
}


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="sb_network",
        description="Statusbar script for network connectivity.",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug output"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    setup_logging(log, logging.DEBUG if args.verbose else logging.ERROR)
    log.debug(args)

    handle_block_button(ACTIONS)

    print(f"{get_wifi_info()}{get_ethernet_info()}{get_vpn_info()}")


if __name__ == "__main__":
    main()

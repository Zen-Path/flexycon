#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
from pathlib import Path

from common.cmd_utilities import run_cmd, run_cmd_background
from common.helpers import NotificationSystem, get_version
from common.logger import logger, setup_logging
from common.statusbar import (
    EDITOR,
    TERMINAL,
    MouseButton,
    handle_block_button,
)


def get_net_state(prefix: str) -> str:
    """Check the operstate of the first interface matching the prefix."""
    try:
        # Finds first match for w*, e*, or tun*
        iface_path = next(Path("/sys/class/net/").glob(f"{prefix}*"), None)
        if iface_path:
            return (iface_path / "operstate").read_text().strip()
    except (StopIteration, PermissionError, FileNotFoundError):
        pass

    return ""


def get_wifi_info() -> str:
    """Returns the WiFi icon and percentage or status icon."""
    state = get_net_state("w")

    if state == "up":
        try:
            with open("/proc/net/wireless", "r") as f:
                for line in f:
                    if line.strip().startswith("w"):
                        # Column 3 is link quality (typically out of 70)
                        quality = float(line.split()[2])
                        percent = int(quality * 100 / 70)
                        return f"📶{percent}% "
        except (IndexError, ValueError, FileNotFoundError):
            return "📶?% "
    elif state == "down":
        try:
            iface_path = next(Path("/sys/class/net/").glob("w*"))
            flags = (iface_path / "flags").read_text().strip()
            # 0x1003 is IFF_UP | IFF_BROADCAST | IFF_MULTICAST
            return "📡 " if flags == "0x1003" else "❌ "
        except (StopIteration, FileNotFoundError):
            return "❌ "

    return ""


def get_ethernet_info() -> str:
    """Returns Ethernet status icon."""
    return "🌐" if get_net_state("e") == "up" else "❎"


def get_vpn_info() -> str:
    """Returns VPN icon if a tun interface is active."""
    # Check if any tun device exists and is not empty
    tun_exists = any(Path("/sys/class/net/").glob("tun*"))
    return " 🔒" if tun_exists else ""


def toggle_wifi() -> None:
    """Toggles WiFi radio status via nmcli."""
    try:
        result = run_cmd(["nmcli", "radio", "wifi"])
        if not result.success:
            return

        new_state = "on" if result.output == "disabled" else "off"
        run_cmd(["nmcli", "radio", "wifi", new_state])

    except Exception as e:
        logger.error(f"Could not toggle wifi: {e}")

    return None


ACTIONS = {
    MouseButton.LEFT: lambda: run_cmd_background([TERMINAL, "-e", "nmtui"]),
    MouseButton.MIDDLE: toggle_wifi,
    MouseButton.RIGHT: lambda: NotificationSystem.run(
        "🌐 Internet",
        "Show internet status.\n"
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
    MouseButton.EXTRA_3: lambda: run_cmd_background([TERMINAL, "-e", EDITOR, __file__]),
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

    setup_logging(logger, logging.DEBUG if args.verbose else logging.ERROR)
    logger.debug(args)

    handle_block_button(ACTIONS)

    print(f"{get_wifi_info()}{get_ethernet_info()}{get_vpn_info()}")


if __name__ == "__main__":
    main()

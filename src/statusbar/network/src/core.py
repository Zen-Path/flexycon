from pathlib import Path
from shutil import which

from common.cmd_utilities import run_cmd, run_cmd_background
from common.logger import log
from common.variables import TERMINAL


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
    """Returns VPN icon if Mullvad is active, falling back to interface check."""
    if which("mullvad"):
        try:
            res = run_cmd(
                ["mullvad", "status"],
            )
            return " 🔒" if res.output.startswith("Connected") else ""
        except Exception:
            pass

    # Check if any tun or wg device exists and is not empty
    vpn_exists = any(Path("/sys/class/net/").glob("tun*")) or any(
        Path("/sys/class/net/").glob("wg*")
    )

    return " 🔒" if vpn_exists else ""


def toggle_wifi() -> None:
    """Toggles WiFi radio status via nmcli."""
    try:
        result = run_cmd(["nmcli", "radio", "wifi"])
        if not result.success:
            return

        new_state = "on" if result.output == "disabled" else "off"
        run_cmd(["nmcli", "radio", "wifi", new_state])

    except Exception as e:
        log.error(f"Could not toggle wifi: {e}")

    return None


def open_network_handlers() -> None:
    run_cmd_background([TERMINAL, "-e", "nmtui"])
    run_cmd_background(["mullvad-vpn"])

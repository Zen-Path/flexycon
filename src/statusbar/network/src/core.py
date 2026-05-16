from pathlib import Path

from common.cmd_utilities import run_cmd
from common.logger import log


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
        log.error(f"Could not toggle wifi: {e}")

    return None

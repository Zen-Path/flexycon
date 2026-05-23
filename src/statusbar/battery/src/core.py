from pathlib import Path

from common.cmd_utilities import run_cmd
from common.logger import log


def adjust_backlight(amount: int) -> None:
    """Adjusts backlight using xbacklight."""
    flag = "-inc" if amount > 0 else "-dec"
    try:
        run_cmd(["xbacklight", flag, abs(amount)])
    except Exception as e:
        log.error(f"Failed to adjust backlight: {e}")


def get_battery_info() -> str:
    batteries = sorted(Path("/sys/class/power_supply/").glob("BAT*"))
    output_parts: list[str] = []

    status_map = {
        "Full": "",
        "Discharging": "",
        "Charging": "",
        "Not charging": "",
        "Unknown": "",
    }

    for battery in batteries:
        try:
            status = (battery / "status").read_text().strip()
            capacity = int((battery / "capacity").read_text().strip())

            icon = status_map.get(status, "")
            warn = ""
            if status == "Discharging" and capacity <= 25:
                warn = ""

            output_parts.append(f"{icon}{warn}{capacity}%")
        except (FileNotFoundError, ValueError) as e:
            log.debug(f"Could not read battery {battery.name}: {e}")
            continue

    return " ".join(output_parts)

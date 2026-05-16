import re
import shutil
from datetime import datetime

from common.cmd_utilities import run_cmd, run_cmd_background
from common.helpers import NotificationSystem
from common.logger import log
from common.statusbar import TERMINAL


def get_calendar() -> str | None:
    """Gets the current calendar and highlights the current day."""
    try:
        current_day = datetime.now().strftime("%-d")
        result = run_cmd(["cal"])
        if not result.success:
            return None

        highlighted = re.sub(
            rf"\b({current_day})\b",
            r"<span color='#1D2021'><b>\1</b></span>",
            result.output,
        )
        return highlighted

    except Exception as e:
        log.error(f"Could not retrieve calendar: {e}")

    return None


def get_appointments() -> str | None:
    """Returns upcoming appointments from calcurse."""
    if not shutil.which("calcurse"):
        log.error(msg="Binary 'calcurse' not found.")
        return None

    try:
        result = run_cmd(["calcurse", "-d3"])
        if not result.success:
            return None

        return result.output if result.output else "No upcoming appointments."

    except Exception as e:
        log.error(f"Could not retrieve appointments: {e}")

    return None


def show_info() -> None:
    """Triggers notifications for both calendar and appointments."""
    NotificationSystem.run("Calendar", get_calendar())

    appointments = get_appointments()
    if appointments:
        NotificationSystem.run("Appointments", appointments)


def open_calcurse() -> None:
    """Opens calcurse in the terminal if installed."""
    if not shutil.which("calcurse"):
        log.error(msg="Binary 'calcurse' not found.")
        return None

    run_cmd_background([TERMINAL, "-e", "calcurse"])

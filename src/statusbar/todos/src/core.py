from common.cmd_utilities import run_cmd
from common.logger import log
from common.notification_utilities import Notification
from common.variables import XDG_DATA_HOME

STATE_FILE = XDG_DATA_HOME / "taskwarrior" / "overdue_tasks"


def get_task_count(filter_str: str) -> int | None:
    """Runs taskwarrior count with the specified filter."""
    try:
        result = run_cmd(["task", filter_str, "count"])
        if not result.success:
            return None

        return int(result.output)
    except Exception as e:
        log.error(f"Could not get task count: {e}")

    return None


def process_tasks() -> str:
    """Processes task counts and handles overdue notifications."""
    # Ensure state directory exists
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Read previous overdue count
    old_overdue = 0
    if STATE_FILE.exists():
        try:
            old_overdue = int(STATE_FILE.read_text().strip())
        except ValueError:
            pass

    # Get current counts
    pending_tasks = get_task_count("+PENDING") or 0
    overdue_tasks = get_task_count("+OVERDUE") or 0
    due_tasks = pending_tasks - overdue_tasks

    # Update state file
    STATE_FILE.write_text(str(overdue_tasks))

    # Notify if more tasks became overdue
    difference = overdue_tasks - old_overdue
    if difference > 0:
        Notification(
            "⚠️ Taskwarrior Alert",
            f"{difference} task{'s' if difference > 1 else ''} become overdue.",
        ).send()

    # Format output
    if overdue_tasks != 0:
        return f"{due_tasks} {overdue_tasks}"
    return f"{due_tasks}"

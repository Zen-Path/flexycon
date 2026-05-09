#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import sys
import threading
import time
from datetime import datetime, timedelta
from typing import Callable

from common.apps.window_manager import Dwm
from common.helpers import (
    Dmenu,
    NotificationSystem,
    PromptOption,
    System,
    get_version,
    run_command,
)
from common.logger import logger, setup_logging


def prompt_user(options: list[PromptOption]) -> str | int | None:
    """Prompt the user and return the selected action ID."""
    lookup = {opt.display_text(): opt.id for opt in options}

    choice = Dmenu.run(
        prompt="System Action", choices=list(lookup.keys()), list_view_item_count=-1
    )

    return lookup.get(choice)


def execute_special_action(action_func: Callable | None = None):
    """
    Handle locking, pausing notifications, tracking time, and ghost-wake prevention.
    If action_func is None, it simply locks the screen.
    """
    if sys.platform != "linux":
        if action_func:
            action_func()
        else:
            System.lock_screen()

        return

    original_notifications_paused_state = NotificationSystem.get_paused() or False
    NotificationSystem.set_paused(True)

    start_time = datetime.now()

    # Turn off Caps Lock just in case
    try:
        xset_out = run_command(["xset", "q"]).output
        if "Caps Lock:   on" in xset_out:
            run_command(["xdotool", "key", "Caps_Lock"])
    except FileNotFoundError:
        logger.debug("'xset' or 'xdotool' not found, skipping Caps Lock check.")

    # Lock the screen asynchronously
    # We must thread this, otherwise the script blocks and never calls sleep()
    def lock_worker():
        System.lock_screen()

    lock_thread = threading.Thread(target=lock_worker, daemon=True)
    lock_thread.start()

    # Give slock a second to initialize
    time.sleep(1)

    # Ghost-wake prevention setup
    watcher_stop_event = threading.Event()

    def ghost_wake_watcher():
        # Wait 45 seconds. If the system was asleep, this pauses and resumes upon wake.
        watcher_stop_event.wait(45.0)
        if not watcher_stop_event.is_set() and lock_thread.is_alive():
            logger.warning("Ghost wake detected. Re-suspending...")
            if action_func:
                action_func()
                ghost_wake_watcher()  # Watch again after the next wake

    # Execute the sleep/hibernate command if provided
    if action_func:
        action_func()
        # Upon waking up, start the ghost watcher
        watcher_thread = threading.Thread(target=ghost_wake_watcher, daemon=True)
        watcher_thread.start()

    # Wait for the user to unlock the screen
    lock_thread.join()

    # User unlocked. Cancel the ghost-wake watcher
    watcher_stop_event.set()

    elapsed_time = datetime.now() - start_time

    if not original_notifications_paused_state:
        NotificationSystem.set_paused(False)

    elapsed_str = str(timedelta(seconds=elapsed_time.total_seconds())).split(".")[0]
    logger.debug(f"Elapsed time: {elapsed_str}")

    NotificationSystem.run(
        title="Welcome back!",
        message=f"You've been gone for {elapsed_str}.",
        urgency="low",
    )


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="system_actions", description="Execute certain system actions."
    )

    subparsers = parser.add_subparsers(dest="action", help="System actions")

    for sp in [
        subparsers.add_parser("sleep", help="Put the system to sleep"),
        subparsers.add_parser("lock", help="Lock the screen"),
        subparsers.add_parser("power-off", help="Power off the system"),
        subparsers.add_parser("reboot", help="Reboot the system"),
        subparsers.add_parser("terminate-wm", help="Terminate the window manager"),
        subparsers.add_parser("refresh-wm", help="Refresh the window manager"),
        subparsers.add_parser("display-off", help="Turn off display"),
        subparsers.add_parser("hibernate", help="Hibernate the system"),
    ]:
        sp.add_argument(
            "-v", "--verbose", action="store_true", help="enable debug output"
        )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    return parser


def main():
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.ERROR)

    wm = Dwm()

    all_options = [
        PromptOption(
            "sleep", "Sleep", "😴", lambda: execute_special_action(System.sleep)
        ),
        PromptOption("lock", "Lock", "🔒", lambda: execute_special_action()),
        PromptOption("power-off", "Power Off", "🔌", System.power_off),
        PromptOption("reboot", "Reboot", "🔄", System.reboot),
        PromptOption("terminate-wm", f"Terminate {wm.display_name}", "☠️", wm.terminate),
        PromptOption("refresh-wm", f"Refresh {wm.display_name}", "♻️", wm.refresh)
        if hasattr(wm, "refresh")
        else None,
        PromptOption(
            "display-off",
            "Display Off",
            "📺",
            lambda: run_command(["xset", "dpms", "force", "off"]),
        ),
        PromptOption(
            "hibernate",
            "Hibernate",
            "🐻",
            lambda: execute_special_action(System.hibernate),
        ),
    ]
    options = list(filter(None, all_options))

    action_id = args.action or prompt_user(options)

    if not action_id:
        return

    selected = next((opt for opt in options if opt.id == action_id), None)

    if selected and selected.action:
        logger.debug(f"Executing {selected.label!r}")
        selected.action()
    else:
        logger.error(f"Action {action_id!r} has no associated function.")


if __name__ == "__main__":
    main()

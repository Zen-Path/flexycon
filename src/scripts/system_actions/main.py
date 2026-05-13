#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import sys
import threading
import time
from datetime import datetime, timedelta
from typing import Callable

from common.apps.window_manager import get_active_window_manager
from common.cmd_utilities import run_cmd
from common.helpers import NotificationSystem, get_version
from common.logger import logger, setup_logging
from common.prompt_utilities import PromptOption, prompt_options
from common.system_utilities import System


def prompt_user(options: list[PromptOption]) -> str | int | None:
    """Prompt the user and return the selected action ID."""
    lookup = {opt.display_text(): opt.id for opt in options}

    result = prompt_options(
        prompt="System Action",
        options=list(lookup.keys()),
        list_view_item_count=-1,
    )

    if result is None:
        return None

    _idx, choice = result

    return lookup.get(choice)


def execute_special_action(action_func: Callable[[], None] | None = None):
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
        xset_out = run_cmd(["xset", "q"]).output
        if "Caps Lock:   on" in xset_out:
            run_cmd(["xdotool", "key", "Caps_Lock"])
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


def build_parser(options: list[PromptOption]) -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    global_parent = argparse.ArgumentParser(add_help=False)
    global_parent.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug output"
    )

    parser = argparse.ArgumentParser(
        prog="system_actions",
        description="Execute certain system actions.",
        parents=[global_parent],
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    # SUBCOMMANDS
    subparsers = parser.add_subparsers(dest="action_id", help="System actions")

    for opt in options:
        subparsers.add_parser(
            str(opt.id),
            parents=[global_parent],
            help=opt.help_text if opt.help_text else "",
        )

    return parser


def main() -> None:
    wm = get_active_window_manager()

    all_options = [
        PromptOption(
            id="sleep",
            label="Sleep",
            symbol="😴",
            help_text="Put the system to sleep",
            action=lambda: execute_special_action(System.sleep),
        ),
        PromptOption(
            id="lock",
            label="Lock",
            symbol="🔒",
            help_text="Lock the screen",
            action=lambda: execute_special_action(),
        ),
        PromptOption(
            id="power-off",
            label="Power Off",
            symbol="🔌",
            help_text="Power off the system",
            action=System.power_off,
        ),
        PromptOption(
            id="reboot",
            label="Reboot",
            symbol="🔄",
            help_text="Reboot the system",
            action=System.reboot,
        ),
        PromptOption(
            id="terminate-wm",
            label=f"Terminate {wm.display_name}",
            symbol="☠️",
            help_text="Terminate the window manager",
            action=wm.terminate,
        )
        if wm
        else None,
        PromptOption(
            id="refresh-wm",
            label=f"Refresh {wm.display_name}",
            symbol="♻️",
            help_text="Refresh the window manager",
            action=getattr(wm, "refresh", None),
        )
        if wm and hasattr(wm, "refresh")
        else None,
        PromptOption(
            id="display-off",
            label="Display Off",
            symbol="📺",
            help_text="Turn off display",
            action=lambda: run_cmd(["xset", "dpms", "force", "off"]),
        ),
        PromptOption(
            id="hibernate",
            label="Hibernate",
            symbol="🐻",
            help_text="Hibernate the system",
            action=lambda: execute_special_action(System.hibernate),
        ),
    ]
    options = list(filter(None, all_options))

    args = build_parser(options).parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.ERROR)
    logger.debug(args)

    action_id = args.action_id or prompt_user(options)

    if not action_id:
        logger.debug("No action was chosen.")
        return

    selected = next((opt for opt in options if opt.id == action_id), None)

    if selected and selected.action:
        logger.debug(f"Executing action {selected.id!r}.")
        selected.action()
    else:
        logger.error(f"Unknown action {action_id!r}.")


if __name__ == "__main__":
    main()

import sys
import threading
import time
from datetime import datetime, timedelta
from typing import Callable

from common.cmd_utilities import run_cmd
from common.helpers import NotificationSystem
from common.logger import log
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
        log.debug("'xset' or 'xdotool' not found, skipping Caps Lock check.")

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
            log.warning("Ghost wake detected. Re-suspending...")
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
    log.debug(f"Elapsed time: {elapsed_str}")

    NotificationSystem.run(
        title="Welcome back!",
        message=f"You've been gone for {elapsed_str}.",
        urgency="low",
    )

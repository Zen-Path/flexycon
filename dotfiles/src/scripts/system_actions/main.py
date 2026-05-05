#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import subprocess
from datetime import datetime, timedelta

from common.apps.window_manager import Dwm
from common.helpers import (
    System,
    get_notifications_paused_status,
    notify,
    set_notifications_status,
)
from common.logger import logger, setup_logging


class SystemAction:
    def __init__(self, name, emoji, function):
        self.name = name
        self.emoji = emoji
        self.function = function

    def __str__(self):
        return f"{self.name} {self.emoji}"

    @classmethod
    def run(cls, action, system):
        """
        Handle the execution of a quick action, managing dunst state and restoring it.
        """
        original_notifications_paused_state = get_notifications_paused_status()
        set_notifications_status("true")

        start_time = datetime.now()

        logger.debug(system.lock_cmd)

        action()
        system.lock_screen()
        # wait_for_display(polling_rate)

        elapsed_time = datetime.now() - start_time

        if not original_notifications_paused_state:
            set_notifications_status("false")

        elapsed_str = str(timedelta(seconds=elapsed_time.total_seconds())).split(".")[0]
        notify(
            title="Welcome back!",
            message=f"You've been gone for {elapsed_str}.",
            urgency="low",
        )


class SystemActionsMenu:
    def __init__(self, actions, prompter="dmenu"):
        self.actions = actions
        self.prompter = prompter
        self.actions_map = {str(action): action.function for action in self.actions}

    def prompt(self, question="System Action"):
        """
        Display a list of actions and return a selected action.
        """
        match self.prompter:
            case "dmenu":
                return self._dmenu_prompt(question)
            case _:
                return None

    # TODO: build a dmenu interface in common
    def _dmenu_prompt(self, question):
        menu_input = "\n".join(self.actions_map.keys())

        choice = subprocess.run(
            ["dmenu", "-i", "-l", "-1", "-p", question],
            input=menu_input,
            text=True,
            capture_output=True,
        ).stdout.strip()

        logger.debug("choice", choice)
        logger.debug(self.actions_map)
        logger.debug(choice in self.actions_map)
        logger.debug(self.actions_map[choice])

        if choice not in self.actions_map:
            return None

        return self.actions_map[choice]


class Display:
    def __init__(self, name=None):
        self.name = name

    # def turn_off(self):


def build_parser():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Execute certain system actions.")

    parser.add_argument("--verbose", action="store_true", help="enable debug output")

    return parser


def main():
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.ERROR)

    window_manger = Dwm()

    system_actions = filter(
        None,
        [
            SystemAction("Sleep", "😴", lambda: System.sleep),
            SystemAction("Lock", "🔒", lambda: System.lock_screen),
            SystemAction("Power Off", "🔌", lambda: System.power_off),
            SystemAction("Reboot", "🔄", lambda: System.reboot),
            SystemAction(
                f"Terminate {window_manger.display_name}",
                "☠️",
                lambda: window_manger.terminate,
            ),
            (
                SystemAction(
                    f"Refresh {window_manger.display_name}",
                    "♻️",
                    lambda: window_manger.refresh(),
                )
                if hasattr(window_manger, "refresh")
                else None
            ),
            # SystemAction("Display Off", "📺", lambda *_:
            #   QuickAction.turn_off_display()),
            SystemAction("Hibernate", "🐻", lambda: System.hibernate),
        ],
    )

    system_actions_menu = SystemActionsMenu(system_actions)
    selected_action = system_actions_menu.prompt()

    logger.debug("selected_action", selected_action)
    if selected_action:
        SystemAction.run(selected_action, System)


if __name__ == "__main__":
    main()

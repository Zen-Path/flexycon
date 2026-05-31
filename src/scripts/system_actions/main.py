#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging

from common.cmd_utilities import run_cmd
from common.helpers import get_version
from common.logger import log, setup_logging
from common.prompt_utilities import PromptOption
from common.system_utilities import System
from common.window_manager_utilities import get_active_window_manager
from scripts.system_actions.src.core import execute_special_action, prompt_user


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

    setup_logging(log, logging.DEBUG if args.verbose else logging.ERROR)
    log.debug(args)

    action_id = args.action_id or prompt_user(options)

    if not action_id:
        log.debug("No action was chosen.")
        return

    selected = next((opt for opt in options if opt.id == action_id), None)

    if selected and selected.action:
        log.debug(f"Executing action {selected.id!r}.")
        selected.action()
    else:
        log.error(f"Unknown action {action_id!r}.")


if __name__ == "__main__":
    main()

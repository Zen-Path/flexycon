#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import os
import shutil
import signal
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

import psutil


def get_parent_process_chain(start_pid=None):
    """
    Traverse the parent chain of the current process (or a given process) and collect
    a list of tuples (process_name, pid).

    Args:
        start_pid (int, optional): PID of the process to start traversal from.
                                   Defaults to the current process.

    Returns:
        list of tuple: [(name, pid), ...]
    """

    process_chain = []
    current_process = psutil.Process(start_pid) if start_pid else psutil.Process()

    while current_process:
        process_chain.append((current_process.name(), current_process.pid))
        current_process = current_process.parent()

    return process_chain


class WindowManager:
    """Base class for window managers."""

    def __init__(self, display_name: str, process_name: str):
        self.display_name = display_name
        self.process_name = process_name
        self.pid = None

    def __repr__(self):
        return f"{self.display_name} ({self.process_name})"

    def terminate(self):
        psutil.Process(self.pid).terminate()

    def fetch_pid(self):
        # TODO: except psutil.NoSuchProcess:
        process_chain = get_parent_process_chain()

        for name, pid in process_chain:
            if name == self.process_name:
                self.pid = pid
                return self.pid

        self.pid = None
        return None


class Dwm(WindowManager):
    def __init__(self):
        super().__init__("DWM", "dwm")

    def refresh(self):
        os.kill(self.pid, signal.SIGHUP)


class I3(WindowManager):
    def __init__(self):
        super().__init__("i3", "i3")


class Openbox(WindowManager):
    def __init__(self):
        super().__init__("Openbox", "openbox")


@dataclass
class System:
    """
    Represents a user-space system.
    """

    controller: Optional[str] = None
    lock_cmd: Optional[str] = None

    def __post_init__(self):
        self.controller = self.controller or self.get_controller()
        self.lock_cmd = self.lock_cmd or self.get_lock_cmd()

    @classmethod
    def get_controller(cls) -> str:
        """
        Determines the system's controller based on the init system in use.
        Returns 'systemctl' if systemd is detected, otherwise 'loginctl'.
        """
        init_path = os.path.realpath("/sbin/init")
        return "systemctl" if "systemd" in init_path else "loginctl"

    def get_lock_cmd(self):
        return "slock" if shutil.which("slock") else None

    def lock_screen(self):
        """Lock the screen."""
        if self.lock_cmd:
            os.system(self.lock_cmd)

    def sleep(self):
        """Put the system to sleep."""
        os.system(f"{self.controller} suspend -i")

    def power_off(self):
        """Power off the system."""
        os.system(f"{self.controller} poweroff -i")

    def reboot(self):
        """Reboot the system."""
        os.system(f"{self.controller} reboot -i")

    def hibernate(self):
        """Hibernate the system."""
        os.system(f"{self.controller} hibernate -i")


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
        original_state = subprocess.getoutput("dunstctl is-paused").strip() == "true"
        subprocess.run(["dunstctl", "set-paused", "true"])

        start_time = datetime.now()

        print(system.lock_cmd)
        action()
        system.lock_screen()
        # wait_for_display(polling_rate)

        elapsed_time = datetime.now() - start_time

        if not original_state:
            subprocess.run(["dunstctl", "set-paused", "false"])

        elapsed_str = str(timedelta(seconds=elapsed_time.total_seconds())).split(".")[0]
        subprocess.run(
            [
                "notify-send",
                "--urgency",
                "low",
                "Welcome back!",
                f"You've been gone for {elapsed_str}.",
            ]
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

    def _dmenu_prompt(self, question):
        menu_input = "\n".join(self.actions_map.keys())

        choice = subprocess.run(
            ["dmenu", "-i", "-l", "-1", "-p", question],
            input=menu_input,
            text=True,
            capture_output=True,
        ).stdout.strip()

        print("choice", choice)
        print(self.actions_map)
        print(choice in self.actions_map)
        print(self.actions_map[choice])
        if choice not in self.actions_map:
            return None

        return self.actions_map[choice]


class Display:
    def __init__(self, name=None):
        self.name = name

    # def turn_off(self):


def main():
    window_manger = Dwm()
    system = System(lock_cmd="slock")
    _ = Display

    system_actions = filter(
        None,
        [
            SystemAction("Sleep", "😴", lambda: system.sleep),
            SystemAction("Lock", "🔒", lambda: system.lock),
            SystemAction("Power Off", "🔌", lambda: system.power_off),
            SystemAction("Reboot", "🔄", lambda: system.reboot),
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
            SystemAction("Hibernate", "🐻", lambda: system.hibernate),
        ],
    )

    system_actions_menu = SystemActionsMenu(system_actions)
    selected_action = system_actions_menu.prompt()

    print("selected_action", selected_action)
    if selected_action:
        SystemAction.run(selected_action, system)


if __name__ == "__main__":
    main()

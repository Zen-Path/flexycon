import os
import signal

import psutil

from common.cmd_utilities import run_cmd
from common.helpers import get_parent_process_chain
from common.logger import log


class WindowManager:
    """Base class for window managers."""

    def __init__(self, display_name: str, process_name: str):
        self.display_name = display_name
        self.process_name = process_name
        self._pid: int | None = None

    @property
    def pid(self) -> int | None:
        """Dynamic PID fetching."""
        if self._pid is None:
            self._pid = self.find_running_pid(self.process_name)

        return self._pid

    @staticmethod
    def find_running_pid(name: str) -> int | None:
        """Checks the process tree for a specific process name."""
        try:
            # Check the parent chain first
            process_chain = get_parent_process_chain()
            for proc_name, pid in process_chain:
                if proc_name == name:
                    return pid

            # Fallback: scan all processes if not in direct parent chain
            for proc in psutil.process_iter(["name"]):  # type: ignore
                if proc.info["name"] == name:
                    return proc.pid
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            log.debug(f"Could not find PID of process {name!r}.")

        return None

    def is_running(self) -> bool:
        return self.pid is not None

    def terminate(self):
        psutil.Process(self._pid).terminate()

    def __repr__(self):
        return f"{self.display_name} ({self.process_name})"


class Dwm(WindowManager):
    def __init__(self):
        super().__init__("DWM", "dwm")

    def refresh(self):
        if self._pid:
            os.kill(self._pid, signal.SIGHUP)


class I3(WindowManager):
    def __init__(self):
        super().__init__("i3", "i3")

    def refresh(self):
        if self.pid:
            run_cmd(["i3-msg", "restart"])


class Openbox(WindowManager):
    def __init__(self):
        super().__init__("Openbox", "openbox")


SUPPORTED_WMS = [Dwm, I3, Openbox]


def get_active_window_manager() -> WindowManager | None:
    """
    Returns an initialized instance of the currently running
    window manager, or None if none are detected.
    """
    for wm_class in SUPPORTED_WMS:
        instance = wm_class()
        if instance.is_running():
            return instance

    return None

import os
import signal

import psutil
from common.helpers import get_parent_process_chain


class WindowManager:
    """Base class for window managers."""

    def __init__(self, display_name: str, process_name: str):
        self.display_name = display_name
        self.process_name = process_name
        self.pid: int | None = None

    def __repr__(self):
        return f"{self.display_name} ({self.process_name})"

    def terminate(self):
        psutil.Process(self.pid).terminate()

    def fetch_pid(self) -> int | None:
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
        if self.pid:
            os.kill(self.pid, signal.SIGHUP)


class I3(WindowManager):
    def __init__(self):
        super().__init__("i3", "i3")


class Openbox(WindowManager):
    def __init__(self):
        super().__init__("Openbox", "openbox")

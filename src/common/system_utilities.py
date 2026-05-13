import os
import shutil
import sys
from dataclasses import dataclass
from typing import Literal

from common.cmd_utilities import run_cmd
from common.logger import logger


def get_display_server() -> Literal["X11", "Wayland"] | None:
    """
    Returns the display server currently in use, or ``None`` if it can't
    be detected.
    """
    display_env_val = os.getenv("DISPLAY")

    if os.getenv("WAYLAND_DISPLAY"):
        return "Wayland"
    elif display_env_val and display_env_val != "needs-to-be-defined":
        return "X11"
    else:
        return None


@dataclass
class ScreenLocker:
    cmd: list[str]
    req_wayland: bool = False
    req_x11: bool = False


class System:
    """
    Represents a user-space system.
    """

    SCREEN_LOCKER_REGISTRY = {
        "slock": ScreenLocker(["slock"], req_x11=True),
        "i3lock": ScreenLocker(["i3lock"], req_x11=True),
        "xlock": ScreenLocker(["xlock"], req_x11=True),
        "swaylock": ScreenLocker(["swaylock"], req_wayland=True),
        "hyprlock": ScreenLocker(["hyprlock"], req_wayland=True),
        "xdg-screensaver": ScreenLocker(["xdg-screensaver", "lock"]),
        "gnome-screensaver": ScreenLocker(["gnome-screensaver-command", "-l"]),
        "loginctl": ScreenLocker(["loginctl", "lock-session"]),
    }

    @classmethod
    def _get_linux_controller(cls) -> Literal["systemctl", "loginctl"] | None:
        """
        Determines the system's controller based on the init system in use.
        Returns 'systemctl' if systemd is detected, otherwise 'loginctl'.
        """
        if sys.platform != "linux":
            logger.warning(f"Method isn't supported for {sys.platform!r}")
            return None

        init_path = os.path.realpath("/sbin/init")
        return "systemctl" if "systemd" in init_path else "loginctl"

    @classmethod
    def _get_lock_cmd(cls) -> list[str] | None:
        """Determines the appropriate lock command based on environment and availability."""
        if sys.platform == "darwin":
            # Note: doesn't immediately lock the screen unless "Require password after
            # screen saver begins or display is turned off" is set to "Immediately" in
            # the user's settings
            return ["pmset", "displaysleepnow"]

        session_type = os.getenv("XDG_SESSION_TYPE", "").lower()
        is_wayland = (session_type == "wayland") or ("WAYLAND_DISPLAY" in os.environ)
        is_x11 = (session_type == "x11") or ("DISPLAY" in os.environ)

        for locker in cls.SCREEN_LOCKER_REGISTRY.values():
            if not shutil.which(locker.cmd[0]):
                continue

            if locker.req_x11 and not is_x11:
                continue

            if locker.req_wayland and not is_wayland:
                continue

            return locker.cmd

        return None

    @classmethod
    def lock_screen(cls):
        """Lock the screen."""
        cmd = cls._get_lock_cmd()
        if cmd:
            run_cmd(cmd)
        else:
            logger.error("No screen locker found.")

    @classmethod
    def sleep(cls):
        """Put the system to sleep."""
        if sys.platform == "darwin":
            run_cmd(["pmset", "sleepnow"])
        elif sys.platform == "linux":
            if cmd := cls._get_linux_controller():
                run_cmd([cmd, "suspend", "-i"])
        else:
            logger.warning(f"Method isn't supported for {sys.platform!r}")

    @classmethod
    def power_off(cls):
        """Power off the system."""
        if sys.platform == "darwin":
            run_cmd(["osascript", "-e", 'tell app "loginwindow" to «event aevtrsdn»'])
        elif sys.platform == "linux":
            if cmd := cls._get_linux_controller():
                run_cmd([cmd, "poweroff", "-i"])
        else:
            logger.warning(f"Method isn't supported for {sys.platform!r}")

    @classmethod
    def reboot(cls):
        """Reboot the system."""
        if sys.platform == "darwin":
            run_cmd(["osascript", "-e", 'tell app "loginwindow" to «event aevtrrst»'])
        elif sys.platform == "linux":
            if cmd := cls._get_linux_controller():
                run_cmd([cmd, "reboot", "-i"])
        else:
            logger.warning(f"Method isn't supported for {sys.platform!r}")

    @classmethod
    def hibernate(cls):
        """Hibernate the system."""
        if sys.platform == "darwin":
            # Standard hibernation isn't exposed gracefully in macOS user-space.
            # We use sleep as a safe default.
            run_cmd(["pmset", "sleepnow"])
        elif sys.platform == "linux":
            if cmd := cls._get_linux_controller():
                run_cmd([cmd, "hibernate", "-i"])
        else:
            logger.warning(f"Method isn't supported for {sys.platform!r}")

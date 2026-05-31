import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal

from common.cmd_utilities import run_cmd, run_cmd_background
from common.logger import log


@dataclass
class Notification:
    title: str
    message: str | None = None
    urgency: Literal["low", "normal", "critical"] = "normal"

    @property
    def title_fmt(self) -> str:
        return self.title.strip().replace("\n", " ")

    @property
    def message_fmt(self) -> str | None:
        return self.message.strip() if self.message else None

    def send(
        self,
        icon_path: Path | None = None,
        callback: Callable[[], None] | None = None,
        open_image_onclick: bool = False,
    ):
        notification_system: type[NotificationSystem] | None = None

        if shutil.which("dunst"):
            notification_system = Dunst
        elif shutil.which("terminal-notifier"):
            notification_system = TerminalNotifier

        if notification_system:
            notification_system.run(self, icon_path, callback, open_image_onclick)
        else:
            log.warning("Unable to find notification system.")


class NotificationSystem(ABC):
    @classmethod
    def run(
        cls,
        notification: Notification,
        icon_path: Path | None = None,
        callback: Callable[[], None] | None = None,
        open_image_onclick: bool = False,
    ):
        """
        Send a desktop notification. Accepts either a custom callback OR
        an action to open the image (icon), but not both.
        """

        # Enforce mutual exclusivity
        if callback and open_image_onclick:
            raise ValueError(
                "You cannot provide both a 'callback' and 'open_image_onclick'."
            )

        log.debug(f"Sending notification: {notification}")

        try:
            result = cls._run(notification, icon_path, callback, open_image_onclick)
            if not result:
                log.warning("Notification failed.")
        except Exception as e:
            log.warning(f"Unable to send notification: {e}")

    @classmethod
    @abstractmethod
    def _run(
        cls,
        notification: Notification,
        icon_path: Path | None = None,
        callback: Callable[[], None] | None = None,
        open_image_onclick: bool = False,
    ) -> bool:
        pass

    @classmethod
    def get_paused(cls) -> bool | None:
        pass

    @classmethod
    def set_paused(cls, status: bool | Literal["toggle"]) -> bool | None:
        pass


class Dunst(NotificationSystem):
    @classmethod
    def _run(
        cls,
        notification: Notification,
        icon_path: Path | None = None,
        callback: Callable[[], None] | None = None,
        open_image_onclick: bool = False,
    ) -> bool:
        cmd: list[str | Path] = [
            "notify-send",
            notification.title_fmt,
            "--urgency",
            notification.urgency,
        ]

        if notification.message_fmt is not None:
            cmd.append(notification.message_fmt)

        if icon_path:
            cmd.extend(["-i", icon_path])

        # Determine which action to use, if any
        action_token = None
        if open_image_onclick and icon_path:
            action_token = "open_image"
            cmd.append(f"--action={action_token}=Open Image")
        elif callback:
            action_token = "custom_callback"
            cmd.append(f"--action={action_token}=Click Me")

        # If no action was defined, fire and forget (non-blocking)
        if not action_token:
            run_cmd_background(cmd)
            return True

        # If an action exists, block and wait for user input
        cmd_output = run_cmd(cmd).output

        if cmd_output == "open_image" and icon_path:
            run_cmd_background(["xdg-open", icon_path])

        elif cmd_output == "custom_callback" and callback:
            callback()

        return True

    @classmethod
    def get_paused(cls) -> bool | None:
        if not shutil.which("dunstctl"):
            return None

        result = run_cmd(["dunstctl", "is-paused"])
        if not result.success:
            return None

        return result.output.strip().lower() == "true"

    @classmethod
    def set_paused(cls, status: bool | Literal["toggle"]) -> bool | None:
        if not shutil.which("dunstctl"):
            return None

        status_str = ""
        if status == "toggle":
            status_str = "toggle"
        else:
            status_str = str(status).lower()

        result = run_cmd(["dunstctl", "set-paused", status_str])
        if not result.success:
            return None

        return result.success


class TerminalNotifier(NotificationSystem):
    @classmethod
    def _run(
        cls,
        notification: Notification,
        icon_path: Path | None = None,
        callback: Callable[[], None] | None = None,
        open_image_onclick: bool = False,
    ) -> bool:
        cmd: list[str | Path] = [
            "terminal-notifier",
            "-title",
            notification.title_fmt,
        ]

        if notification.message_fmt is not None:
            cmd.extend(["-message", notification.message_fmt])

        if icon_path:
            cmd.extend(["-appIcon", icon_path.as_uri()])

        if open_image_onclick and icon_path:
            cmd.extend(["-contentImage", icon_path.as_uri()])
            cmd.extend(["-open", icon_path.as_uri()])

        if notification.urgency == "critical":
            cmd.append("-ignoreDnD")

        run_cmd_background(cmd)

        return True

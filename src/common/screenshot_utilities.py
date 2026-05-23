from datetime import datetime
from pathlib import Path
from typing import Literal

from common.cmd_utilities import run_cmd
from common.helpers import Color, NotificationSystem, Window
from common.logger import log
from common.variables import XDG_PICTURES_DIR


class Maim:
    @classmethod
    def run(
        cls,
        output_path: Path,
        select: bool = False,
        border_size: float = 4.0,
        padding: float = 0.0,
        tolerance: float = 20.0,
        color: Color = Color(100.0, 0.0, 0.0, 0.3),
        no_decorations: int = 2,
        hide_cursor: bool = True,
        quiet: bool = True,
        delay: float = 0.2,
        window: Window | None = None,
    ) -> bool:
        """
        Take screenshot of desktop and save to an image.
        """
        cmd = [
            "maim",
            f"--bordersize={border_size}",
            f"--padding={padding}",
            f"--tolerance={tolerance}",
            f"--color={color}",
            f"--nodecorations={no_decorations}",
        ]
        if hide_cursor:
            cmd.append("--hidecursor")
        if quiet:
            cmd.append("--quiet")
        if window:
            cmd.extend(["--window", str(window.id), "--capturebackground"])

        if select:
            cmd.extend(["--select", "--nodrag", "--highlight"])

        cmd.extend(["--delay", str(delay)])
        cmd.append(str(output_path))

        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            return run_cmd(cmd).success

        except FileNotFoundError:
            log.error("Binary 'maim' not found.")
            return False

        except Exception as e:
            log.error(f"Command failed: {e}")
            return False


class ScreenshotUtility:
    OUTPUT_DIR = XDG_PICTURES_DIR / "Screenshots"

    @classmethod
    def _capture(
        cls,
        output_path: Path,
        copy_output: bool,
        select: bool = False,
        window: Window | None = None,
    ):
        success = Maim.run(output_path, select, window=window)

        if success and copy_output:
            # TODO: temporary, until sorting common logic structure to avoid circular
            # dependencies
            from common.packages.clipboard_utilities import copy_file

            copy_file(output_path)
            NotificationSystem.run(
                "Screenshot captured",
                f"Saved at {str(output_path)!r}",
                icon_path=output_path,
                open_image_onclick=True,
            )

        return success

    @classmethod
    def _compose_output_path(
        cls,
        capture_type: Literal["area", "window", "screen", "full"],
        output_dir: Path | None = None,
        name: str = "",
        ext: str = "png",
        include_timestamp: bool = True,
    ) -> Path:
        """Generate a file path to the output directory with the current timestamp."""
        name_fmt = name[:100]
        timestamp_fmt = (
            datetime.now().strftime("%Y-%m-%d_%H-%M-%S") if include_timestamp else ""
        )

        filename = "_".join(
            [part for part in [timestamp_fmt, name_fmt, capture_type] if part]
        )

        return Path(
            output_dir or cls.OUTPUT_DIR,
            f"{filename}.{ext}".lower(),
        )

    @classmethod
    def area(
        cls,
        output_dir: Path | None = None,
        copy_output: bool = False,
    ) -> bool:
        """Capture a selected area."""
        output_path = cls._compose_output_path("area", output_dir=output_dir)
        return cls._capture(output_path, copy_output, select=True)

    @classmethod
    def window(
        cls,
        window: Window | None = None,
        include_window_name: bool = False,
        output_dir: Path | None = None,
        copy_output: bool = False,
    ) -> bool:
        """Capture a window."""
        if window is None:
            window = Window.get_active_window()

        # If no window found, capture the screen
        if window is None:
            return cls.screen(output_dir=output_dir, copy_output=copy_output)

        window_name = ""
        if include_window_name:
            window_name = Window.get_window_name(window.id) or ""

        output_path = cls._compose_output_path(
            "window", name=window_name, output_dir=output_dir
        )

        return cls._capture(output_path, copy_output, window=window)

    @classmethod
    def screen(
        cls,
        screen: int | None = None,
        output_dir: Path | None = None,
        copy_output: bool = False,
    ) -> bool:
        """Capture a screen."""
        # TODO: Implement logic for targeting a single screen
        output_path = cls._compose_output_path("screen", output_dir=output_dir)
        return cls._capture(output_path, copy_output)

    @classmethod
    def full_screen(
        cls,
        output_dir: Path | None = None,
        copy_output: bool = False,
    ) -> bool:
        """Capture all screens."""
        output_path = cls._compose_output_path("full", output_dir=output_dir)
        return cls._capture(output_path, copy_output)

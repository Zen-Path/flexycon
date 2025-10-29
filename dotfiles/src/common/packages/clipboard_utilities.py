import subprocess

from common.helpers import run_command
from common.packages.models import ClipboardUtility


class XClip(ClipboardUtility):
    command = "xclip"

    @classmethod
    def text(cls, text: str):
        subprocess.run([cls.command, "-sel", "clip"], input=text.encode(), check=True)

    @classmethod
    def file(cls, file_path: str):
        run_command(
            [cls.command, "-sel", "clip", "-t", "image/png", "-i", file_path],
        )


class XSel(ClipboardUtility):
    command = "xsel"

    @classmethod
    def text(cls, text: str):
        subprocess.run(
            [cls.command, "--clipboard", "--input"], input=text.encode(), check=True
        )

    @classmethod
    def file(cls, file_path: str):
        run_command([cls.command, "--clipboard", "--input", file_path])

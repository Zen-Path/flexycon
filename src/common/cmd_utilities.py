import secrets
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from common.logger import log


@dataclass
class CommandResult:
    return_code: int
    raw_output: str

    @property
    def output(self) -> str:
        return self.raw_output.strip()

    @property
    def success(self) -> bool:
        return self.return_code == 0

    def __str__(self) -> str:
        return self.output


def run_cmd(command: Sequence[str | int | Path]) -> CommandResult:
    """Run a shell command and return its result."""
    cmd_identifier = secrets.token_hex(5)  # 8 hex chars

    normalized_cmd = [str(p) if not isinstance(p, str) else p for p in command]
    log.debug(f"Running {normalized_cmd} with id {cmd_identifier!r}")

    output: list[str] = []
    with subprocess.Popen(
        normalized_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
    ) as process:
        if process.stdout is not None:
            for line in process.stdout:
                output.append(line)  # newline is included
                log.debug(line.strip())

        return_code = process.wait()

    log.debug(
        f"Command with id {cmd_identifier!r} finished with return code {return_code}"
    )

    return CommandResult(return_code=return_code, raw_output="".join(output))


def run_cmd_background(command: Sequence[str | int | Path]):
    """Run a command in the background."""

    normalized_cmd = [str(p) if not isinstance(p, str) else p for p in command]
    log.debug(f"Running {normalized_cmd} in background.")

    subprocess.Popen(
        normalized_cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,  # detach from the current process group (Unix)
        shell=False,
    )

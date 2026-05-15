import secrets
import subprocess
from dataclasses import dataclass

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


def run_cmd(command: list[str]) -> CommandResult:
    """Run a shell command and return its result."""
    cmd_identifier = secrets.token_hex(5)  # 8 hex chars

    log.debug(f"Running {command} with id {cmd_identifier!r}")

    output: list[str] = []
    with subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
    ) as process:
        if process.stdout is not None:
            for line in process.stdout:
                output.append(line)
                log.debug(line.strip())

        return_code = process.wait()

    log.debug(
        f"Command with id {cmd_identifier!r} finished with return code {return_code}"
    )

    return CommandResult(return_code=return_code, raw_output="\n".join(output))


def run_cmd_background(command: list[str]):
    """Run a command in the background."""
    log.debug(f"Running {command} in background.")

    subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,  # detach from the current process group (Unix)
        shell=False,
    )

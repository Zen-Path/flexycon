import logging
import os
import subprocess
from typing import List, Tuple

logger = logging.getLogger(__name__)


def resolve_path(path_parts: List[str]) -> str:
    """Resolve a list of path parts into a single expanded string path."""
    return os.path.expandvars(os.path.join(*path_parts))


def run_command(command: List[str]) -> Tuple[int, List[str]]:
    """Run a shell command."""
    logger.info(f"Running: {command}")
    print(command)

    output = []
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
                logger.info(line.strip())

        returncode = process.wait()

    logger.info(f"Command ({command}) finished with return code {returncode}")
    return returncode, output

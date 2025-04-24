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


def prompt_user(prompt, positive_resp=["y"], negative_resp=["n"], default="n"):
    possible_resp = positive_resp + negative_resp
    if default not in possible_resp:
        return False

    default_index = possible_resp.index(default)
    possible_resp[default_index] = possible_resp[default_index].upper()

    try:
        user_resp = input(f"> {prompt} ({'/'.join(possible_resp)}): ").strip().lower()
    except KeyboardInterrupt:
        exit()

    return user_resp in positive_resp


def ensure_directory_interactive(path):
    if not os.path.exists(path):
        print(f":: The directory '{path}' does not exist.")
        user_resp = prompt_user("Would you like to create the directory?")
        if user_resp:
            os.makedirs(path)
        else:
            print(":: Operation cancelled by user.")
            sys.exit(1)

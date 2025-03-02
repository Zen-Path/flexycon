import logging
import subprocess
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def run_command(command: list[str]) -> int:
    """
    Execute a shell command with error handling.

    Parameters:
        command: The command and its arguments to execute.

    Returns:
        int: The exit code of the command.
    """

    command_fmt = " ".join(command)
    logging.info(f"Running command: '{command_fmt}'")

    result = subprocess.run(
        command, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr
    )

    logging.info(
        f"Command finished - command: '{command_fmt}'; returncode: {result.returncode}"
    )
    return result.returncode

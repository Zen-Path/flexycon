#!/usr/bin/env python3

import argparse
import logging
import re
import sys
from pprint import pprint

from colorama import Fore, Style, init
from tabulate import tabulate

# Initialize colorama
init(autoreset=True)


# Custom formatter for colorful logging
class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": Fore.BLUE,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, "")
        reset = Style.RESET_ALL
        message = super().format(record)
        return f"{color}{message}{reset}"


# Function to process lines
def process_line(line):
    logging.debug(f"{line.strip()}")
    match = re.search(
        r"NOTICE: (.*): Skipped (copy|delete|update|remove directory|set directory modification time) as --dry-run is set( \(size (.*)\))?",
        line,
    )

    if not match:
        return None

    filepath, mod_type, size = None, None, 0
    if match:
        groups = match.groups()
        logging.debug(f"Match groups: {groups}")
        filepath = groups[0]
        mod_type = groups[1]
        if groups[3]:
            size = groups[3]

    if mod_type == "set directory modification time":
        mod_type = "dir mod time"

    return [mod_type, filepath, size]


def main():
    parser = argparse.ArgumentParser(
        description="Process log files and output skipped operations."
    )
    parser.add_argument(
        "file",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="File to process (default: stdin)",
    )
    parser.add_argument(
        "-V", "--verbose", action="store_true", help="Increase output verbosity"
    )

    args = parser.parse_args()

    # Configure logging
    handler = logging.StreamHandler()
    handler.setFormatter(
        ColorFormatter(
            fmt="%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
        )
    )
    root = logging.getLogger()
    root.addHandler(handler)
    if args.verbose:
        root.setLevel(logging.DEBUG)
    else:
        root.setLevel(logging.CRITICAL)  # Suppress logging by default

    output = []

    with args.file as f:
        for line in f:
            processed_line = process_line(line)
            if processed_line:
                output.append(processed_line)

    filename_max_size = 100
    action_fmt = {
        "delete": Fore.RED,
        "remove directory": Fore.RED,
        "copy": Fore.YELLOW,
        "dir mod time": Fore.BLUE,
    }

    sorted_data = sorted(output, key=lambda x: (x[0], x[1], x[2]))

    if sorted_data:
        formatted_output = []
        change_type_counter = {}

        for row in sorted_data:
            formatted_row = [
                (action_fmt[row[0]] if row[0] in action_fmt else Fore.GRAY)
                + row[0]
                + Style.RESET_ALL,
                Fore.CYAN + row[1][:filename_max_size] + Style.RESET_ALL,
                Fore.MAGENTA + str(row[2]) + Style.RESET_ALL,
            ]
            formatted_output.append(formatted_row)

            change_type_counter[row[0]] = change_type_counter.setdefault(row[0], 0) + 1

        print(
            Style.BRIGHT
            + tabulate(
                formatted_output,
                headers=["Type", "Filepath", "Size"],
                tablefmt="simple_outline",
            )
        )

        pprint(change_type_counter)

    else:
        print(Fore.RED + "No relevant entries found.")


if __name__ == "__main__":
    main()

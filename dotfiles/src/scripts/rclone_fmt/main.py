#!/usr/bin/env python3

import argparse
import logging
import re
import sys
from pprint import pprint

from colorama import Fore, Style, init
from common.logger import logger, setup_logging
from tabulate import tabulate

# Initialize colorama
init(autoreset=True)


# Function to process lines
def process_line(line):
    logger.debug(f"{line.strip()}")
    match = re.search(
        r"NOTICE: (.*): Skipped (copy|delete|update|remove directory|set directory modification time) as --dry-run is set( \(size (.*)\))?",
        line,
    )

    if not match:
        return None

    filepath, mod_type, size = None, None, 0
    if match:
        groups = match.groups()
        logger.debug(f"Match groups: {groups}")
        filepath = groups[0]
        mod_type = groups[1]
        if groups[3]:
            size = groups[3]

    if mod_type == "set directory modification time":
        mod_type = "dir mod time"

    return [mod_type, filepath, size]


def build_parser():
    parser = argparse.ArgumentParser(
        description="Process rclone output and display a structured report on changes and operations."
    )

    parser.add_argument(
        "file",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="file to process (default: stdin)",
    )
    parser.add_argument("--verbose", action="store_true", help="enable debug output")

    return parser


def main():
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.WARNING)

    output = []

    with args.file as f:
        try:
            for line in f:
                processed_line = process_line(line)
                if processed_line:
                    output.append(processed_line)
        except:
            print(f)

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

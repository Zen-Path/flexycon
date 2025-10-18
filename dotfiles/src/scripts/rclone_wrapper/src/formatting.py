from typing import Any, Dict, List

import humanize
from colorama import Fore, Style, init
from common.helpers import truncate
from tabulate import tabulate

init(autoreset=True)


def print_table(data, headers):
    print(tabulate(data, headers=headers, tablefmt="simple_outline"))


def format_operations(
    operations_data: List[Dict[str, Any]], filename_max_size: int = 100
) -> List[List[str]]:
    """
    Format rclone operations for display in a table.
    """
    # Define colors for operation types
    ACTIONS_FMT = {
        "copy": Fore.GREEN,
        "move": Fore.YELLOW,
        "delete": Fore.RED,
        "dir remove": Fore.MAGENTA,
        "dir make": Fore.BLUE,
        "dir mod time": Fore.CYAN,
    }

    # Normalize type names
    TYPE_REMAP = {
        "set directory modification time": "dir mod time",
        "remove directory": "dir remove",
        "make directory": "dir make",
    }

    # Sort operations by type, then file, then size (numerically)
    sorted_data = sorted(
        operations_data, key=lambda x: (x["type"], x["file"], int(x["size"]))
    )

    formatted_result = []

    for op in sorted_data:
        op_type = str(op.get("type") or "")
        op_file = str(op.get("file") or "")
        op_size = int(op.get("size") or 0)

        # Remap types
        op_type = TYPE_REMAP.get(op_type, op_type)

        # Special handling for moves
        if op_type.startswith("move to"):
            destination = op_type.replace("move to ", "")
            op_file = f"{op_file} -> {destination}"
            op_type = "move"

        # Determine size color
        if op_size > 100_000_000:
            size_color = Fore.RED
        elif op_size > 1_000_000:
            size_color = Fore.YELLOW
        else:
            size_color = Fore.GREEN

        # Build formatted row
        row = [
            ACTIONS_FMT.get(op_type, Fore.LIGHTBLACK_EX) + op_type + Style.RESET_ALL,
            Fore.WHITE
            + truncate(op_file, filename_max_size, truncate_start=True)
            + Style.RESET_ALL,
            Fore.MAGENTA + humanize.naturalsize(op_size) + Style.RESET_ALL,
            size_color + str(op_size) + Style.RESET_ALL,
        ]

        formatted_result.append(row)

    return formatted_result


def format_stats(stats):
    result = {}

    result["bytes"] = (
        f"{humanize.naturalsize(int(stats['bytes']))} / {humanize.naturalsize(int(stats['totalBytes']))}"
    )
    result["transfers"] = f"{stats['transfers']} / {stats['totalTransfers']}"
    result["checks"] = f"{stats['checks']} / {stats['totalChecks']}"

    for field in [
        "listed",
        "deletedDirs",
        "deletes",
        "renames",
        "errors",
        "fatalError",
        "retryError",
        "elapsedTime",
    ]:
        result[field] = stats[field]

    return result

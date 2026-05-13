import humanize
from colorama import Fore, Style, init
from common.string_utilities import truncate
from scripts.rclone_wrapper.src.models import (
    OperationStyle,
    ProcessedOperation,
    RcloneOperation,
    RcloneStats,
)
from tabulate import tabulate

init(autoreset=True)


OPERATION_REGISTRY: dict[str, OperationStyle] = {
    "copy": OperationStyle(short_name="copy", color=Fore.GREEN),
    "move": OperationStyle(short_name="move", color=Fore.YELLOW),
    "delete": OperationStyle(short_name="delete", color=Fore.LIGHTRED_EX),
    "update modification time": OperationStyle(
        short_name="update mod time", color=Fore.BLUE
    ),
    "remove directory": OperationStyle(short_name="dir remove", color=Fore.RED),
    "make directory": OperationStyle(short_name="dir make", color=Fore.MAGENTA),
    "set directory modification time": OperationStyle(
        short_name="dir mod time", color=Fore.LIGHTBLUE_EX
    ),
}


def print_table(data: list[list[str]], headers: list[str]):
    print(tabulate(data, headers=headers, tablefmt="simple_outline"))


def resolve_operation_info(raw_type: str) -> tuple[str, str, str | None]:
    """Resolves raw rclone 'skipped' type to (short_name, color, destination)"""
    if raw_type.startswith("move to "):
        dest = raw_type.replace("move to ", "")
        return "move", Fore.YELLOW, dest

    style = OPERATION_REGISTRY.get(raw_type)
    if style:
        return style.short_name, style.color, None

    return raw_type, Fore.LIGHTBLACK_EX, None


def transform_operations(raw_ops: list[RcloneOperation]) -> list[ProcessedOperation]:
    processed: list[ProcessedOperation] = []

    for op in raw_ops:
        short_name, color, destination = resolve_operation_info(op.raw_type)
        processed.append(
            ProcessedOperation(
                display_type=short_name,
                display_file=op.raw_file,
                size=op.size,
                color=color,
                destination=destination,
            )
        )

    return processed


def prepare_table_rows(
    ops: list[ProcessedOperation], max_width: int = 100
) -> list[list[str]]:
    sorted_ops = sorted(ops, key=lambda x: (x.display_type, x.display_file, x.size))

    rows: list[list[str]] = []
    for op in sorted_ops:
        file_path = (
            f"'{op.display_file}' -> '{op.destination}'"
            if op.destination
            else op.display_file
        )

        if op.size > 100_000_000:
            size_color = Fore.RED
        elif op.size > 1_000_000:
            size_color = Fore.YELLOW
        else:
            size_color = Fore.GREEN

        row = [
            f"{op.color}{op.display_type}{Style.RESET_ALL}",
            f"{Fore.WHITE}{truncate(file_path, max_width, truncate_from_end=False)}{Style.RESET_ALL}",
            f"{Fore.MAGENTA}{humanize.naturalsize(op.size)}{Style.RESET_ALL}",
            f"{size_color}{op.size}{Style.RESET_ALL}",
        ]
        rows.append(row)

    return rows


def ratio_fmt(current: int | float, total: int | float, is_size: bool = False) -> str:
    if is_size:
        return (
            f"{humanize.naturalsize(int(current))} / {humanize.naturalsize(int(total))}"
        )
    return f"{current} / {total}"


def alert_fmt(value: int | bool) -> str:
    if value:
        return f"{Fore.RED}{value}{Style.RESET_ALL}"
    return str(value)


def format_stats(stats: RcloneStats) -> list[list[str]]:
    """
    Transforms stats into formatted rows for table display.
    """
    display_map = [
        ("Bytes Transferred", ratio_fmt(stats.bytes, stats.total_bytes, is_size=True)),
        ("Transfers", ratio_fmt(stats.transfers, stats.total_transfers)),
        ("Checks", ratio_fmt(stats.checks, stats.total_checks)),
        ("Listed", stats.listed),
        ("Directories Deleted", stats.deleted_dirs),
        ("Files Deleted", stats.deletes),
        ("Renames", stats.renames),
        ("Errors", alert_fmt(stats.errors)),
        ("Fatal Error", alert_fmt(stats.fatal_error)),
        ("Retry Error", alert_fmt(stats.retry_error)),
        ("Elapsed Time", f"{stats.elapsed_time:.2f}s"),
    ]

    return [[str(label), str(val)] for label, val in display_map]

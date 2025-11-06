#!/usr/bin/env python3

import re
from argparse import ArgumentParser, ArgumentTypeError, Namespace
from datetime import datetime, timedelta


def parse_abs_date(date_str: str) -> datetime:
    """
    Parse a date string containing exactly three runs of digits, interpreted
    as YYYY<sep>MM<sep>DD — in that order. Separator can be any non-digit char.
    Raises ValueError if you don't get exactly 3 groups of digits or if they
    don't form a valid YYYY-MM-DD date.
    """
    parts = re.findall(r"\d+", date_str)
    if len(parts) != 3:
        raise ArgumentTypeError(
            f"Invalid date format in {date_str!r}: found {len(parts)} numeric groups, "
            "but expected exactly 3 (YYYY, MM, DD)."
        )

    year, month, day = parts
    if len(year) != 4:
        raise ArgumentTypeError(
            f"Invalid year component {year!r} in {date_str!r}: "
            f"year must have exactly 4 digits, but has {len(year)}."
        )

    try:
        return datetime(int(year), int(month), int(day))
    except ValueError as ve:
        # month out of range, day out of range, etc.
        raise ArgumentTypeError(f"Invalid date components in {date_str!r}: {ve}")


def add_date_args(parser: ArgumentParser):
    """
    Add an --absolute flag and a required positional DATE argument.
    """
    parser.add_argument(
        "-a",
        "--absolute",
        action="store_true",
        dest="is_date_absolute",
        help=(
            "interpret DATE as an absolute date. "
            "Format: YYYY<sep>MM<sep>DD. <sep> is any non-digit char. "
            "Example: '2025-01-01'"
        ),
    )

    parser.add_argument(
        "date_value",
        nargs="?",
        default=None,
        metavar="DATE",
        help="an absolute or relative date. If omitted, uses the current date",
    )


def resolve_date(args: Namespace) -> datetime:
    """
    Determine the target date from parsed command-line arguments.

    This function expects the provided Namespace to define both
    `date_value` and `is_date_absolute` attributes.

    - If `args.date_value` is ``None``, the current date and time are used.
    - If `args.is_date_absolute` is ``True``, the value is parsed as an
      absolute date string.
    - Otherwise, the value is interpreted as a relative day offset from now.
      For example, ``-1`` means yesterday, and ``3`` means three
      days from today.
    """
    required_attrs = ("date_value", "is_date_absolute")
    missing = [name for name in required_attrs if not hasattr(args, name)]
    if missing:
        raise ArgumentTypeError(
            f"Missing required argument attributes on Namespace: {', '.join(missing)}. "
        )

    target_date = None
    if args.date_value is None:
        target_date = datetime.now()
    elif args.is_date_absolute:
        target_date = parse_abs_date(args.date_value)
    else:
        # Default to relative mode
        try:
            target_date = datetime.now() + timedelta(days=int(args.date_value))
        except ValueError:
            raise ArgumentTypeError(
                f"Invalid relative offset {args.date_value!r}: expected an integer, "
                "such as -1 for yesterday or 3 for three days from now."
            )

    return target_date

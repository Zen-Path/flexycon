#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import json
import logging
from pathlib import Path

import commentjson

from common.helpers import get_version
from common.logger import log, setup_logging


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="jsonc_to_json",
        description="Convert a jsonc file to json.",
    )

    parser.add_argument("input_file", type=Path, help="the jsonc file")

    parser.add_argument("output_file", type=Path, help="the resulting json file")

    parser.add_argument(
        "-i",
        "--indentation",
        type=int,
        default=4,
        help=("specify the number of spaces used for the json file's indentation"),
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug output"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    return parser


def main() -> None:
    args = build_parser().parse_args()

    setup_logging(log, logging.DEBUG if args.verbose else logging.WARNING)
    log.debug(args)

    with open(args.input_file, "r") as f:
        data = commentjson.load(f)  # type: ignore

    with open(args.output_file, "w") as f:
        json.dump(data, f, indent=args.indentation)


if __name__ == "__main__":
    main()

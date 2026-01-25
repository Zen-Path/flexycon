#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import json
import logging

import commentjson
from common.logger import logger, setup_logging


def build_parser():
    parser = argparse.ArgumentParser(description="Convert a jsonc file to json.")

    parser.add_argument("input_file", help="the jsonc file")

    parser.add_argument("output_file", help="the resulting json file")

    parser.add_argument(
        "-i",
        "--indentation",
        type=int,
        default=4,
        help=("specify the number of spaces used for the json file's indentation"),
    )

    parser.add_argument("--verbose", action="store_true", help="enable debug output")

    return parser


def main():
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.WARNING)

    with open(args.input_file, "r") as f:
        data = commentjson.load(f)

    with open(args.output_file, "w") as f:
        json.dump(data, f, indent=args.indentation)


if __name__ == "__main__":
    main()

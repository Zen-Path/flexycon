#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging

from common.args import add_date_args, resolve_date
from common.helpers import get_version
from common.logger import log, setup_logging
from scripts.git_logs.data.repos import GIT_REPOS
from scripts.git_logs.src.core import compose_output


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="git_logs",
        description="List Git commits in a repo for all branches by a date.",
    )

    add_date_args(parser)

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

    target_date = resolve_date(args)
    log.info(f"Target date: {target_date.strftime('%Y-%m-%d')}")

    git_repos_str = "\n".join([str(r) for r in GIT_REPOS])
    log.debug(f"Git Repos (count: {len(GIT_REPOS)}):\n{git_repos_str}")

    print(compose_output(target_date, GIT_REPOS))


if __name__ == "__main__":
    main()

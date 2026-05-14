#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import traceback
from datetime import datetime

from git import InvalidGitRepositoryError, Repo

from common.args import add_date_args, resolve_date
from common.helpers import get_version
from common.logger import logger, setup_logging
from scripts.git_logs.src.repos import GIT_REPOS


def get_main_branch(repo: Repo) -> str | None:
    for name in ["main", "master"]:
        if name in repo.heads:
            return name
    return None


def get_commit_messages_on_date(
    repo: Repo,
    branch_name: str,
    date: datetime,
    exclude_commits: set[str] = set(),
) -> list[str]:
    date_str = date.strftime("%Y-%m-%d")

    messages: list[str] = []
    seen: set[str] = set()
    for commit in repo.iter_commits(branch_name):
        if commit.hexsha in exclude_commits:
            continue
        commit_date = datetime.fromtimestamp(commit.authored_date).date()
        if commit_date.isoformat() == date_str:
            if commit.hexsha not in seen:
                commit_summary = commit.summary
                commit_summary_str = (
                    bytes.decode(commit_summary)
                    if isinstance(commit_summary, bytes)
                    else commit_summary
                )
                messages.append(f"- {commit_summary_str}")
                seen.add(commit.hexsha)

    return messages


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

    setup_logging(logger, logging.DEBUG if args.verbose else logging.WARNING)
    logger.debug(args)

    target_date = resolve_date(args)
    logger.info(f"Target date: {target_date.strftime('%Y-%m-%d')}\n")

    all_repo_outputs: list[str] = []

    for git_repo in GIT_REPOS:
        if not git_repo.path.exists():
            continue

        try:
            repo = Repo(git_repo.path)
            main_branch = get_main_branch(repo)
            if not main_branch:
                continue

            repo_sections: list[str] = []

            main_commits = list(repo.iter_commits(main_branch))
            main_commit_shas = {c.hexsha for c in main_commits}

            main_messages = get_commit_messages_on_date(repo, main_branch, target_date)
            if main_messages:
                branch_block = f"\n{'\n'.join(main_messages)}"
                repo_sections.append(branch_block)

            # For the other branches, we only want to see commits that aren't also
            # on the main branch.
            for branch in repo.heads:
                if branch.name == main_branch:
                    continue
                messages = get_commit_messages_on_date(
                    repo, branch.name, target_date, exclude_commits=main_commit_shas
                )
                if messages:
                    branch_block = f"### {branch.name}\n" + "\n".join(messages)
                    repo_sections.append(branch_block)

            if repo_sections:
                repo_block = f"## {git_repo.name}\n" + "\n\n".join(repo_sections)
                all_repo_outputs.append(repo_block)

        except InvalidGitRepositoryError as e:
            logger.warning(f"{type(e).__name__}: {e}")

        except Exception as e:
            logger.error(e)
            logger.debug(traceback.format_exc())

    if all_repo_outputs:
        print("\n\n".join(all_repo_outputs))


if __name__ == "__main__":
    main()

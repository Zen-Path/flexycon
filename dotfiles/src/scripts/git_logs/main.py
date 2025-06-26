import argparse
import logging
import traceback
from datetime import datetime

from common.args import format_help_choices
from common.date_args import add_date_args, resolve_date
from common.logger import setup_logging
from git import InvalidGitRepositoryError, Repo
from scripts.git_logs.src.repos import GIT_REPOS

logger = logging.getLogger(__name__)


def get_main_branch(repo):
    for name in ["main", "master"]:
        if name in repo.heads:
            return name
    return None


def get_commit_messages_on_date(repo, branch_name, date, exclude_commits=set()):
    date_str = date.strftime("%Y-%m-%d")

    messages = []
    seen = set()
    for commit in repo.iter_commits(branch_name):
        if commit.hexsha in exclude_commits:
            continue
        commit_date = datetime.fromtimestamp(commit.authored_date).date()
        if commit_date.isoformat() == date_str:
            if commit.hexsha not in seen:
                messages.append(f"- {commit.summary}")
                seen.add(commit.hexsha)

    return messages


def parse_args():
    parser = argparse.ArgumentParser(
        description="List Git commits in a repo for all branches by a date."
    )

    add_date_args(parser, format_help_choices)

    parser.add_argument("--verbose", action="store_true", help="enable debug output")

    return parser.parse_args()


def main():
    args = parse_args()

    setup_logging(verbose=args.verbose)

    target_date = resolve_date(args)
    logger.info(f"Target date: {target_date.strftime("%Y-%m-%d")}\n")

    all_repo_outputs = []

    for git_repo in GIT_REPOS:
        if not git_repo.path.exists():
            continue

        try:
            repo = Repo(git_repo.path)
            main_branch = get_main_branch(repo)
            if not main_branch:
                continue

            repo_sections = []

            main_commits = list(repo.iter_commits(main_branch))
            main_commit_shas = {c.hexsha for c in main_commits}

            main_messages = get_commit_messages_on_date(repo, main_branch, target_date)
            if main_messages:
                branch_block = f"\n{"\n".join(main_messages)}"
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

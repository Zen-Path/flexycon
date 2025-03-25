import argparse
import os
from datetime import datetime
from pathlib import Path

from git import Repo

# Human-readable repo names to Path (you can use ~ or $HOME)
REPOS = {
    "flexycon": "/home/link/.local/src/flexycon",
    "Journal": "~/Personal/No_Backup/Journal",
    "DWM": "~/.local/src/dwm",
}


def expand_path(path):
    return Path(os.path.expandvars(os.path.expanduser(str(path)))).resolve()


def get_main_branch(repo):
    for name in ["main", "master"]:
        if name in repo.heads:
            return name
    return None


def get_commit_messages_on_date(repo, branch_name, date_str, exclude_commits=set()):
    messages = []
    seen = set()
    for commit in repo.iter_commits(branch_name):
        if commit.hexsha in exclude_commits:
            continue
        commit_date = datetime.fromtimestamp(commit.committed_date).date()
        if commit_date.isoformat() == date_str:
            if commit.hexsha not in seen:
                messages.append(f"- {commit.summary}")
                seen.add(commit.hexsha)
        elif commit_date < datetime.fromisoformat(date_str).date():
            break
    return messages


def main():
    parser = argparse.ArgumentParser(
        description="List Git commits by date, with main branch first."
    )
    parser.add_argument("date", help="Date in YYYY-MM-DD format")
    args = parser.parse_args()

    try:
        datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
        return

    all_repo_outputs = []

    for repo_name, raw_path in REPOS.items():
        repo_path = expand_path(raw_path)
        if not repo_path.exists():
            continue

        try:
            repo = Repo(repo_path)
            main_branch = get_main_branch(repo)
            if not main_branch:
                continue

            repo_sections = []

            main_commits = list(repo.iter_commits(main_branch))
            main_commit_shas = {c.hexsha for c in main_commits}

            main_messages = get_commit_messages_on_date(repo, main_branch, args.date)
            if main_messages:
                branch_block = f"### {main_branch}\n" + "\n".join(main_messages)
                repo_sections.append(branch_block)

            for branch in repo.heads:
                if branch.name == main_branch:
                    continue
                messages = get_commit_messages_on_date(
                    repo, branch.name, args.date, exclude_commits=main_commit_shas
                )
                if messages:
                    branch_block = f"### {branch.name}\n" + "\n".join(messages)
                    repo_sections.append(branch_block)

            if repo_sections:
                repo_block = f"## {repo_name}\n" + "\n\n".join(repo_sections)
                all_repo_outputs.append(repo_block)

        except Exception as e:
            print(f"Error processing '{repo_name}': {e}")

    if all_repo_outputs:
        print("\n\n".join(all_repo_outputs))


if __name__ == "__main__":
    main()

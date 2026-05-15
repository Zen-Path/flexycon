import traceback
from datetime import datetime

from git import InvalidGitRepositoryError, Repo

from common.helpers import resolve_path
from common.logger import log


class GitRepo:
    def __init__(self, name: str, path_parts: list[str]):
        self.name = name
        self.path_parts = path_parts
        self.path = resolve_path(self.path_parts)

    def __str__(self):
        return f"GitRepo(name={self.name!r}, path={str(self.path)!r})"


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


def compose_output(target_date: datetime, git_repos: list[GitRepo]) -> str:
    all_repo_outputs: list[str] = []

    for git_repo in git_repos:
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
            log.warning(f"{type(e).__name__}: {e}")

        except Exception as e:
            log.error(e)
            log.debug(traceback.format_exc())

    return "\n\n".join(all_repo_outputs)

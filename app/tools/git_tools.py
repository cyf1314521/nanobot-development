import subprocess
from pathlib import Path

from app.config import settings


class GitToolError(Exception):
    pass


def _run_git(args: list[str], workspace_root: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=workspace_root,
        capture_output=True,
        text=True,
        timeout=settings.tool_timeout_seconds,
    )
    if result.returncode != 0:
        raise GitToolError((result.stderr or result.stdout).strip())
    return result.stdout.strip()


def create_branch(workspace_root: str, branch_name: str) -> str:
    return _run_git(["checkout", "-b", branch_name], workspace_root)


def get_diff(workspace_root: str) -> str:
    return _run_git(["diff"], workspace_root)


def summarize_diff(workspace_root: str) -> str:
    try:
        return _run_git(["diff", "--stat"], workspace_root)
    except GitToolError:
        return "No diff available."


def is_git_repo(workspace_root: str) -> bool:
    return (Path(workspace_root) / ".git").exists()

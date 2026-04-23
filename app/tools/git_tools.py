import subprocess
from pathlib import Path

from app.config import settings

# Git 工具层统一异常，便于上层捕获并做错误分类
class GitToolError(Exception):
    pass


def _run_git(
    args: list[str],
    workspace_root: str,
    timeout_seconds: int | None = None,
) -> str:
    """
    在指定仓库目录执行 git 子命令，并返回标准输出。
    例如：
    args=["diff"] -> 实际执行 git diff
    未传 timeout 时使用 settings.tool_timeout_seconds。
    """
    if timeout_seconds is None:
        timeout_seconds = settings.tool_timeout_seconds
    result = subprocess.run(
        ["git", *args],            # 组装完整命令：git + 参数
        cwd=workspace_root,        # 指定仓库根目录执行
        capture_output=True,       # 捕获 stdout/stderr
        text=True,                 # 以字符串形式处理输出
        timeout=timeout_seconds,   # 超时保护，避免命令卡死
    )

    # 非 0 退出码视为失败，抛出统一异常
    if result.returncode != 0:
        raise GitToolError((result.stderr or result.stdout).strip())

    return result.stdout.strip()


def is_git_repo(workspace_root: str) -> bool:
    """
    判断指定路径是否为 git 仓库（通过 .git 目录判断）。
    """
    return (Path(workspace_root) / ".git").exists()


def create_branch(workspace_root: str, branch_name: str) -> str:
    """
    创建并切换到新分支：git checkout -b <branch_name>
    """
    return _run_git(["checkout", "-b", branch_name], workspace_root)


def get_diff(workspace_root: str) -> str:
    """
    获取当前工作区未提交改动的完整 diff。
    """
    return _run_git(["diff"], workspace_root)


def summarize_diff(workspace_root: str) -> str:
    """
    获取 diff 的统计摘要（文件变更行数等）。
    """
    return _run_git(["diff", "--stat"], workspace_root)
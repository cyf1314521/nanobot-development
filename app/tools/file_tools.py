from pathlib import Path


class FileToolError(Exception):
    """文件工具统一异常类型。"""
    pass


def _resolve_and_validate(root: Path, relative_path: str) -> Path:
    """
    解析相对路径并校验目标是否仍在仓库根目录内，防止目录穿越攻击。
    """
    target = (root / relative_path).resolve()
    root = root.resolve()

    # target 必须是 root 本身或其子路径
    if target != root and root not in target.parents:
        raise FileToolError(f"Path outside workspace is not allowed: {relative_path}")

    return target


def read_file_safe(workspace_root: str, relative_path: str) -> str:
    """
    安全读取文件（仅允许 workspace_root 内部路径）。
    """
    root = Path(workspace_root)
    target = _resolve_and_validate(root, relative_path)

    if not target.exists():
        raise FileToolError(f"File does not exist: {relative_path}")
    if not target.is_file():
        raise FileToolError(f"Target is not a file: {relative_path}")

    return target.read_text(encoding="utf-8")


def write_file_safe(workspace_root: str, relative_path: str, content: str) -> None:
    """
    安全写入文件（仅允许 workspace_root 内部路径）。
    不存在则自动创建父目录与文件。
    """
    root = Path(workspace_root)
    target = _resolve_and_validate(root, relative_path)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
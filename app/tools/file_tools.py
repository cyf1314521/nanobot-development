from pathlib import Path


class FileToolError(Exception):
    pass


def _resolve_and_validate(root: Path, target: str) -> Path:
    resolved = (root / target).resolve()
    root_resolved = root.resolve()
    if root_resolved not in resolved.parents and resolved != root_resolved:
        raise FileToolError(f"Path outside workspace is not allowed: {target}")
    return resolved


def read_file_safe(workspace_root: str, rel_path: str) -> str:
    root = Path(workspace_root)
    target = _resolve_and_validate(root, rel_path)
    if not target.exists():
        raise FileToolError(f"File does not exist: {rel_path}")
    return target.read_text(encoding="utf-8")


def write_file_safe(workspace_root: str, rel_path: str, content: str) -> None:
    root = Path(workspace_root)
    target = _resolve_and_validate(root, rel_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

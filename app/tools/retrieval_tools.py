from pathlib import Path

from app.config import settings
from app.tools.file_tools import FileToolError, read_file_safe


def _safe_read(workspace_root: str, rel_path: str, max_chars: int = 1500) -> str:
    """安全读取单文件并截断，避免上下文过长。"""
    try:
        content = read_file_safe(workspace_root, rel_path)
        return content[:max_chars]
    except FileToolError:
        return ""


def _knowledge_dir_chunks(
    workspace_root: str,
    knowledge_dir_rel: str,
    *,
    max_files: int = 12,
    max_chars: int = 1500,
) -> list[str]:
    """从 workspace 下的知识库目录收集片段（.md / .txt / .rst）。"""
    root = Path(workspace_root).resolve()
    kdir = (root / knowledge_dir_rel).resolve()
    if not kdir.is_dir():
        return []
    try:
        kdir.relative_to(root)
    except ValueError:
        return []

    chunks: list[str] = []
    paths: list[Path] = []
    for p in sorted(kdir.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix.lower() not in (".md", ".txt", ".rst"):
            continue
        # 防止路径跳脱 workspace（解析后必须在 root 下）
        try:
            p.resolve().relative_to(root)
        except ValueError:
            continue
        paths.append(p)

    for p in paths[:max_files]:
        rel = p.relative_to(root).as_posix()
        snippet = _safe_read(workspace_root, rel, max_chars)
        if snippet:
            chunks.append(f"[{rel}]\n{snippet}")
    return chunks


def retrieve_project_context(
    workspace_root: str | None = None,
    *,
    include_knowledge_dir: bool = True,
) -> list[str]:
    """
    最小 RAG：从关键文件 + 可选知识库目录提取上下文。
    未传 workspace_root 时使用 settings.workspace_root；知识库路径为
    {workspace_root}/{settings.knowledge_dir}。
    """
    if workspace_root is None:
        workspace_root = settings.workspace_root

    candidates = [
        "README.md",
        "app/main.py",
        "app/graph/workflow.py",
        "app/schemas/state.py",
        "tests/test_health.py",
    ]
    chunks: list[str] = []
    for path in candidates:
        snippet = _safe_read(workspace_root, path)
        if snippet:
            chunks.append(f"[{path}]\n{snippet}")

    if include_knowledge_dir:
        chunks.extend(
            _knowledge_dir_chunks(workspace_root, settings.knowledge_dir)
        )
    return chunks

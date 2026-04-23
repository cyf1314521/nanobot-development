from app.tools.file_tools import FileToolError, read_file_safe


def _safe_read(workspace_root: str, rel_path: str, max_chars: int = 1500) -> str:
    """安全读取单文件并截断，避免上下文过长。"""
    try:
        content = read_file_safe(workspace_root, rel_path)
        return content[:max_chars]
    except FileToolError:
        return ""


def retrieve_project_context(workspace_root: str = ".") -> list[str]:
    """
    最小 RAG：从关键文件提取上下文片段。
    先用固定文件列表，后续可替换为向量检索。
    """
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
    return chunks

from app.schemas.state import TaskState
from app.tools.file_tools import FileToolError, read_file_safe, write_file_safe


def run_coder(state: TaskState) -> TaskState:
    """
    Coder 职责：
    1) 生成 patch 草案
    2) 在受控模式下尝试落盘（演示用）
    3) 失败时回滚并记录错误
    """
    if not state.plan:
        state.errors.append("Planner output missing: state.plan is None.")
        return state

    # 先保留草案输出（用于 PR 展示）
    state.code_patch = (
        "### Proposed Patch Draft\n"
        f"- Requirement: {state.requirement}\n"
        "- Locate related modules and existing tests.\n"
        "- Implement minimal code changes to satisfy acceptance criteria.\n"
        "- Add or update tests if behavior changes.\n"
        "- Keep backward compatibility unless requirement says otherwise.\n"
    )

    # 受控演示：仅当需求里包含关键词时，尝试改写 tmp/demo.txt
    # 这样你可以演示“自动写文件 + 回滚”，又不会动核心代码
    should_apply = "apply_demo_patch" in state.requirement.lower()
    if not should_apply:
        return state

    workspace_root = "."
    target_file = "tmp/demo.txt"
    backup_content = None

    try:
        try:
            backup_content = read_file_safe(workspace_root, target_file)
        except FileToolError:
            # 文件不存在也允许，视为首次创建
            backup_content = None

        new_content = (
            "This file was updated by Coder Agent.\n"
            f"task_id={state.task_id}\n"
            f"requirement={state.requirement}\n"
        )
        write_file_safe(workspace_root, target_file, new_content)

    except Exception as exc:
        # 回滚逻辑：如果原来有内容就恢复；没有则写空占位
        try:
            if backup_content is not None:
                write_file_safe(workspace_root, target_file, backup_content)
        except Exception:
            pass

        state.errors.append(f"Coder apply failed and rolled back: {exc}")

    return state
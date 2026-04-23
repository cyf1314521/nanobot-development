from app.schemas.state import TaskState


def run_coder(state: TaskState) -> TaskState:
    """
    Coder 的职责：
    1) 读取 planner 给出的计划
    2) 生成代码变更草案（当前阶段先不直接改文件）
    3) 写回 state.code_patch
    """
    if not state.plan:
        state.errors.append("Planner output missing: state.plan is None.")
        return state

    # 当前先做“可解释草案”，第 2 阶段再升级成真正 patch apply + 回滚
    state.code_patch = (
        "### Proposed Patch Draft\n"
        f"- Requirement: {state.requirement}\n"
        "- Locate related modules and existing tests.\n"
        "- Implement minimal code changes to satisfy acceptance criteria.\n"
        "- Add or update tests if behavior changes.\n"
        "- Keep backward compatibility unless requirement says otherwise.\n"
    )

    return state
from app.schemas.actions import ActionPlan, ActionType, AgentAction
from app.schemas.state import TaskState


def run_planner(state: TaskState) -> TaskState:
    """
    Planner 的职责：
    1) 把用户需求拆成可执行步骤
    2) 给出验收标准
    3) 写回 state.plan
    """
    plan = ActionPlan(
        task_id=state.task_id,
        steps=[
            AgentAction(
                type=ActionType.retrieve_context,
                reason="Collect relevant docs and code snippets first.",
            ),
            AgentAction(
                type=ActionType.propose_patch,
                reason="Propose code changes to satisfy the requirement.",
            ),
            AgentAction(
                type=ActionType.run_tests,
                reason="Run tests to verify behavior and reduce regressions.",
            ),
            AgentAction(
                type=ActionType.summarize,
                reason="Create structured PR summary for final output.",
            ),
        ],
        acceptance_criteria=[
            "Task requirement is addressed by the code patch.",
            "Selected tests pass.",
            "Final response includes PR-oriented summary.",
        ],
    )
    state.plan = plan
    return state

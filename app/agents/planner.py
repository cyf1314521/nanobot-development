import json

from app.llm.client import get_llm
from app.schemas.actions import ActionPlan, ActionType, AgentAction
from app.schemas.state import TaskState
from app.tools.retrieval_tools import retrieve_project_context


def _fallback_plan(state: TaskState) -> ActionPlan:
    # 当 LLM 不可用或解析失败时，使用稳定的兜底计划
    return ActionPlan(
        task_id=state.task_id,
        steps=[
            AgentAction(
                type=ActionType.retrieve_context,
                reason="Collect relevant docs and existing code context first.",
                params={"sources": ["README.md", "app/", "tests/"]},
            ),
            AgentAction(
                type=ActionType.propose_patch,
                reason="Propose minimal safe code changes to satisfy requirement.",
                params={"strategy": "minimal-change"},
            ),
            AgentAction(
                type=ActionType.run_tests,
                reason="Run tests to validate behavior and reduce regressions.",
                params={"command": state.test_command},
            ),
            AgentAction(
                type=ActionType.summarize,
                reason="Generate PR-ready summary for review and merge.",
                params={"format": "markdown"},
            ),
        ],
        acceptance_criteria=[
            "The requirement is addressed by proposed code changes.",
            "Relevant tests pass successfully.",
            "Output includes PR-ready summary.",
        ],
    )


def run_planner(state: TaskState) -> TaskState:
    # 第一步先收集项目上下文，供后续 Planner/Coder 参考
    state.context = retrieve_project_context()

    # 优先尝试 LLM 生成动态计划
    llm = get_llm()
    if llm is None:
        state.plan = _fallback_plan(state)
        return state

    # 要求模型严格返回 JSON，便于直接反序列化为 ActionPlan
    prompt = f"""
You are a software planning agent.
Return JSON ONLY with this shape:
{{
  "task_id": "<string>",
  "steps": [
    {{"type":"retrieve_context|propose_patch|run_tests|summarize","reason":"<string>","params":{{}}}}
  ],
  "acceptance_criteria": ["<string>"]
}}

Task:
- task_id: {state.task_id}
- requirement: {state.requirement}
- test_command: {state.test_command}
- context_snippets: {state.context[:3]}
"""
    try:
        resp = llm.invoke(prompt)
        # 将模型响应解析为结构化计划
        data = json.loads(resp.content)
        state.plan = ActionPlan(**data)
    except Exception as exc:
        # 任意异常都回退到模板计划，保证流程可继续
        state.errors.append(f"LLM planner failed, fallback used: {exc}")
        state.plan = _fallback_plan(state)

    return state

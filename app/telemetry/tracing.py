import time
from typing import Callable

from app.schemas.state import TaskState


def _clip(text: str, limit: int = 220) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def _build_input_summary(state: TaskState) -> dict:
    return {
        "task_id": state.task_id,
        "requirement": _clip(state.requirement, 120),
        "context_count": len(state.context),
        "error_count": len(state.errors),
    }


def _build_output_summary(node_name: str, state: TaskState) -> dict:
    if node_name == "planner":
        return {
            "planned_steps": len(state.plan.steps) if state.plan else 0,
            "acceptance_criteria_count": len(state.plan.acceptance_criteria) if state.plan else 0,
        }
    if node_name == "coder":
        return {"code_patch_preview": _clip(state.code_patch or "", 180)}
    if node_name == "tester":
        report = state.test_report
        return {
            "test_command": report.command if report else state.test_command,
            "passed": report.passed if report else False,
            "exit_code": report.exit_code if report else None,
        }
    if node_name == "reviewer":
        return {
            "findings_count": len(state.review_findings),
            "risk_levels": [f.level.value for f in state.review_findings],
        }
    return {}


def with_trace(node_name: str, fn: Callable[[TaskState], TaskState]) -> Callable[[TaskState], TaskState]:
    """为节点函数添加执行轨迹记录。"""

    def wrapped(state: TaskState) -> TaskState:
        started = time.perf_counter()
        input_summary = _build_input_summary(state)
        before_errors = len(state.errors)

        out_state = fn(state)

        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        new_errors = out_state.errors[before_errors:]
        trace = {
            "node": node_name,
            "latency_ms": elapsed_ms,
            "input_summary": input_summary,
            "output_summary": _build_output_summary(node_name, out_state),
            "new_errors": new_errors,
        }
        out_state.traces.append(trace)
        return out_state

    return wrapped

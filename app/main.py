from fastapi import FastAPI
from pydantic import BaseModel

from app.graph.workflow import build_workflow
from app.schemas.state import TaskState

app = FastAPI(title="Multi-Agent Dev Assistant")
workflow = build_workflow()


class RunRequest(BaseModel):
    task_id: str
    requirement: str
    test_command: str = "pytest -q"


@app.get("/health")
def health() -> dict:
    """
    健康检查接口
    """
    return {"status": "ok"}


@app.post("/run")
def run_task(req: RunRequest) -> dict:
    """
    执行一次多 Agent 工作流
    """
    input_state = TaskState(
        task_id=req.task_id,
        requirement=req.requirement,
        test_command=req.test_command,
    )

    output_state = workflow.invoke(input_state)

    # output_state 可能是 TaskState 或 dict，统一转成 dict 返回
    if hasattr(output_state, "model_dump"):
        return output_state.model_dump()
    return output_state
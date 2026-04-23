from fastapi import FastAPI
from pydantic import BaseModel

from app.graph.workflow import build_workflow
from app.schemas.state import TaskState

# FastAPI 应用入口
app = FastAPI(title="Multi-Agent Dev Assistant")
# 应用启动时编译一次工作流，后续请求复用
workflow = build_workflow()


class RunRequest(BaseModel):
    # 任务唯一标识
    task_id: str
    # 用户自然语言需求
    requirement: str
    # 测试命令（默认使用 pytest）
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
    # 组装初始状态，交给工作流逐节点处理
    input_state = TaskState(
        task_id=req.task_id,
        requirement=req.requirement,
        test_command=req.test_command,
    )

    # 执行完整流程：planner -> coder -> tester -> reviewer
    output_state = workflow.invoke(input_state)

    # output_state 可能是 TaskState 或 dict，统一转成 dict 返回
    if hasattr(output_state, "model_dump"):
        return output_state.model_dump()
    return output_state
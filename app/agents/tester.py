from app.schemas.actions import TestReport
from app.schemas.state import TaskState
from app.tools.test_tools import run_test_command


def run_tester(state: TaskState) -> TaskState:
    """
    Tester 的职责：
    1) 执行测试命令
    2) 把结果转成 TestReport
    3) 写回 state.test_report
    """
    # 执行测试（默认来自 state.test_command）
    report_dict = run_test_command(state.test_command)

    # 用 Pydantic 模型约束输出结构
    state.test_report = TestReport(**report_dict)
    return state
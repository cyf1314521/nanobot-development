from langgraph.graph import END, StateGraph

from app.agents.coder import run_coder
from app.agents.planner import run_planner
from app.agents.reviewer import run_reviewer
from app.agents.tester import run_tester
from app.schemas.state import TaskState


def build_workflow():
    """
    构建多 Agent 工作流：
    planner -> coder -> tester -> reviewer -> END
    """
    graph = StateGraph(TaskState)

    # 注册节点
    graph.add_node("planner", run_planner)
    graph.add_node("coder", run_coder)
    graph.add_node("tester", run_tester)
    graph.add_node("reviewer", run_reviewer)

    # 设置入口
    graph.set_entry_point("planner")

    # 连线
    graph.add_edge("planner", "coder")
    graph.add_edge("coder", "tester")
    graph.add_edge("tester", "reviewer")
    graph.add_edge("reviewer", END)

    return graph.compile()
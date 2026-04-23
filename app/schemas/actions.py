from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# Agent 可执行动作类型（统一动作词表）
class ActionType(str, Enum):
    # 读取文件内容
    read_file = "read_file"
    # 生成代码补丁（草案或可应用 patch）
    propose_patch = "propose_patch"
    # 运行测试命令
    run_tests = "run_tests"
    # 产出总结（如 PR 文案）
    summarize = "summarize"
    # 创建分支
    create_branch = "create_branch"
    # 获取代码差异
    get_diff = "get_diff"
    # 检索上下文（RAG）
    retrieve_context = "retrieve_context"
    # 审查变更风险
    review_changes = "review_changes"


# 单个动作的标准结构
class AgentAction(BaseModel):
    # 动作类型（必须来自 ActionType）
    type: ActionType
    # 选择该动作的原因，便于追踪与审计
    reason: str = Field(description="Why this action is selected.")
    # 动作参数，具体键值由工具定义
    params: Dict[str, Any] = Field(default_factory=dict)


# Planner 输出的整体验证计划
class ActionPlan(BaseModel):
    # 任务唯一标识
    task_id: str
    # 按顺序执行的动作列表
    steps: List[AgentAction] = Field(default_factory=list)
    # 验收条件列表
    acceptance_criteria: List[str] = Field(default_factory=list)


# Tester 输出的测试报告
class TestReport(BaseModel):
    # 执行的测试命令
    command: str
    # 是否通过
    passed: bool
    # 进程退出码（0 通常代表成功）
    exit_code: int
    # 标准输出和错误输出合并内容
    output: str


# Reviewer 风险等级
class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


# 单条审查发现
class ReviewFinding(BaseModel):
    # 问题标题
    title: str
    # 风险级别
    level: RiskLevel
    # 问题详情
    details: str
    # 建议修复方案（可选）
    suggestion: Optional[str] = None


# 最终 PR 描述结构（可直接渲染到模板）
class PRDescription(BaseModel):
    # 变更摘要
    summary: str
    # 具体改动点
    changes: List[str] = Field(default_factory=list)
    # 测试计划
    test_plan: List[str] = Field(default_factory=list)
    # 已知风险
    risks: List[str] = Field(default_factory=list)

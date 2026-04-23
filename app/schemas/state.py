from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.actions import ActionPlan, PRDescription, ReviewFinding, TestReport


class TaskState(BaseModel):
    # 当前任务唯一 ID
    task_id: str
    # 用户输入的原始需求
    requirement: str

    # RAG 或上下文检索得到的片段
    context: List[str] = Field(default_factory=list)

    # Planner 产出的结构化执行计划
    plan: Optional[ActionPlan] = None

    # Coder 产出的 patch 草案（后面会升级为可自动应用）
    code_patch: Optional[str] = None

    # Tester 要执行的命令（默认 pytest）
    test_command: str = "pytest -q"
    # Tester 产出的结构化报告
    test_report: Optional[TestReport] = None

    # Reviewer 产出的风险发现
    review_findings: List[ReviewFinding] = Field(default_factory=list)

    # 最终 PR 文案
    pr_description: Optional[PRDescription] = None

    # 运行追踪信息（后面用于 trace/metrics）
    traces: List[Dict[str, Any]] = Field(default_factory=list)

    # 记忆笔记（短期/长期记忆先预留字段）
    memory_notes: List[str] = Field(default_factory=list)

    # 执行过程中出现的错误
    errors: List[str] = Field(default_factory=list)
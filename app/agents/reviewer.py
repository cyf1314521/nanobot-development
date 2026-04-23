from app.schemas.actions import PRDescription, ReviewFinding, RiskLevel
from app.schemas.state import TaskState


def run_reviewer(state: TaskState) -> TaskState:
    """
    Reviewer 的职责：
    1) 根据测试结果给风险判断
    2) 生成结构化 review_findings
    3) 生成 PRDescription（供后续直接展示/提交）
    """
    findings: list[ReviewFinding] = []

    # 测试失败 => 高风险
    if state.test_report and not state.test_report.passed:
        findings.append(
            ReviewFinding(
                title="Tests are failing",
                level=RiskLevel.high,
                details="Automated tests did not pass. Merging now may introduce regressions.",
                suggestion="Fix failing tests before creating or merging PR.",
            )
        )
    # 有改动草案且测试通过/未执行 => 给中风险提醒
    elif state.code_patch:
        findings.append(
            ReviewFinding(
                title="Manual review recommended",
                level=RiskLevel.medium,
                details="Patch draft exists; please verify code style, edge cases, and compatibility.",
                suggestion="Run lint checks and inspect changed files manually.",
            )
        )

    state.review_findings = findings

    # 生成 PR 文案（当前用基础模板，后面可升级成 LLM 生成）
    state.pr_description = PRDescription(
        summary=f"Auto-generated implementation for: {state.requirement}",
        changes=[state.code_patch or "No patch draft generated."],
        test_plan=[state.test_command],
        risks=[f"{f.level.value}: {f.title}" for f in findings] if findings else ["low: no critical risks found"],
    )

    return state
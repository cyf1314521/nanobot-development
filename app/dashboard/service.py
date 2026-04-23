import json
from pathlib import Path
from typing import Any, Dict


def load_latest_eval_report(report_path: str = "eval/reports/latest.json") -> Dict[str, Any]:
    """加载最新评测报告，不存在时返回空结构。"""
    path = Path(report_path)
    if not path.exists():
        return {
            "summary": {
                "total_tasks": 0,
                "success_rate": 0.0,
                "test_pass_rate": 0.0,
                "avg_latency_ms": 0.0,
            },
            "results": [],
        }
    return json.loads(path.read_text(encoding="utf-8"))


def load_dashboard_template(template_path: str = "app/dashboard/templates/eval_dashboard.html") -> str:
    """读取可视化页面模板。"""
    path = Path(template_path)
    return path.read_text(encoding="utf-8")


def load_latest_run(report_path: str = "eval/reports/latest_run.json") -> Dict[str, Any]:
    """加载最近一次 /run 结果，用于展示 Agent 执行轨迹。"""
    path = Path(report_path)
    if not path.exists():
        return {"traces": [], "task_id": None, "requirement": None}
    return json.loads(path.read_text(encoding="utf-8"))

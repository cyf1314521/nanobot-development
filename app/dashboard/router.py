from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.dashboard.service import load_dashboard_template, load_latest_eval_report, load_latest_run

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/eval/latest")
def get_latest_eval() -> dict:
    """返回最新评测 JSON 数据。"""
    return load_latest_eval_report()


@router.get("/run/latest")
def get_latest_run() -> dict:
    """返回最近一次 /run 的完整结果（含 traces）。"""
    return load_latest_run()


@router.get("", response_class=HTMLResponse)
def eval_dashboard() -> str:
    """评测可视化页面入口。"""
    return load_dashboard_template()

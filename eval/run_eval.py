import argparse
import json
import time
from pathlib import Path
from statistics import mean

import httpx
import yaml


def load_tasks(path: Path) -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data.get("tasks", [])


def run_one(client: httpx.Client, base_url: str, task: dict) -> dict:
    started = time.perf_counter()
    response = client.post(
        f"{base_url}/run",
        json={
            "task_id": task["task_id"],
            "requirement": task["requirement"],
            "test_command": task.get("test_command", "python -m pytest -q"),
        },
        timeout=120,
    )
    elapsed_ms = (time.perf_counter() - started) * 1000

    ok = response.status_code == 200
    payload = response.json() if ok else {"errors": [response.text]}
    errors = payload.get("errors", [])
    test_report = payload.get("test_report") or {}
    test_passed = bool(test_report.get("passed", False))

    return {
        "task_id": task["task_id"],
        "status_code": response.status_code,
        "elapsed_ms": round(elapsed_ms, 2),
        "success": ok and len(errors) == 0,
        "test_passed": test_passed,
        "errors": errors,
    }


def summarize(results: list[dict]) -> dict:
    if not results:
        return {
            "total_tasks": 0,
            "success_rate": 0.0,
            "test_pass_rate": 0.0,
            "avg_latency_ms": 0.0,
        }

    total = len(results)
    success_count = sum(1 for r in results if r["success"])
    test_pass_count = sum(1 for r in results if r["test_passed"])
    avg_latency = mean(r["elapsed_ms"] for r in results)
    return {
        "total_tasks": total,
        "success_rate": round(success_count / total, 4),
        "test_pass_rate": round(test_pass_count / total, 4),
        "avg_latency_ms": round(avg_latency, 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run benchmark tasks against /run API.")
    parser.add_argument(
        "--benchmarks",
        default="eval/benchmarks.yaml",
        help="Path to benchmark yaml file.",
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="API base url.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit number of tasks for quick check. 0 means all.",
    )
    args = parser.parse_args()

    tasks = load_tasks(Path(args.benchmarks))
    if args.limit > 0:
        tasks = tasks[: args.limit]

    if not tasks:
        raise SystemExit("No benchmark tasks found.")

    results: list[dict] = []
    with httpx.Client() as client:
        for task in tasks:
            print(f"Running {task['task_id']} ...")
            result = run_one(client, args.base_url, task)
            results.append(result)
            print(
                f"  status={result['status_code']} success={result['success']} "
                f"test_passed={result['test_passed']} latency_ms={result['elapsed_ms']}"
            )

    summary = summarize(results)
    report = {"summary": summary, "results": results}

    report_dir = Path("eval/reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "latest.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n=== Eval Summary ===")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    main()

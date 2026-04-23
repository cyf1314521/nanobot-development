import subprocess

from app.config import settings


def run_test_command(command: str, timeout_seconds: int | None = None) -> dict:
    """
    执行测试命令并返回结构化结果。未传 timeout 时使用 settings.tool_timeout_seconds。
    """
    if timeout_seconds is None:
        timeout_seconds = settings.tool_timeout_seconds
    try:
        # 调用子进程执行测试命令：
        # - shell=True: 允许直接传字符串命令（如 "pytest -q"）
        # - capture_output=True: 捕获 stdout/stderr，便于后续写入报告
        # - text=True: 以字符串形式返回输出（而不是 bytes）
        # - timeout: 防止命令卡死
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )

        # 合并标准输出和错误输出，统一放入 output 字段
        output = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")

        # 返回统一结构，供 Tester Agent 转成 TestReport
        return {
            "command": command,  # 执行的命令
            "passed": result.returncode == 0,  # 退出码为 0 视为成功
            "exit_code": result.returncode,  # 真实退出码
            "output": output.strip(),  # 去掉首尾空白，方便展示
        }

    except subprocess.TimeoutExpired:
        # 超时统一返回 124（常见超时退出码约定），并标记为失败
        return {
            "command": command,
            "passed": False,
            "exit_code": 124,
            "output": f"Command timed out after {timeout_seconds}s",
        }
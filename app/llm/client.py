import os
from pathlib import Path
from typing import Optional

from langchain_openai import ChatOpenAI  # pyright: ignore[reportMissingImports]
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]

# 自动加载项目根目录的 .env，避免每次手动导出环境变量
_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_ROOT / ".env")


def get_llm() -> Optional[ChatOpenAI]:
    # 未配置密钥时返回 None，让上层走 fallback 逻辑
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    # 兼容 OpenAI 风格网关（例如 NVIDIA integrate）
    model = os.getenv("OPENAI_MODEL", "meta/llama-3.1-70b-instruct")
    base_url = os.getenv("OPENAI_BASE_URL")
    return ChatOpenAI(model=model, temperature=0, base_url=base_url)

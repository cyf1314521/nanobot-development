from typing import Optional

from langchain_openai import ChatOpenAI  # pyright: ignore[reportMissingImports]

from app.config import settings


def get_llm() -> Optional[ChatOpenAI]:
    # 未配置密钥时返回 None，让上层走 fallback 逻辑
    if not settings.openai_api_key:
        return None

    kwargs: dict = {
        "model": settings.model_name,
        "temperature": 0,
        "api_key": settings.openai_api_key,
    }
    if settings.openai_base_url:
        kwargs["base_url"] = settings.openai_base_url
    return ChatOpenAI(**kwargs)

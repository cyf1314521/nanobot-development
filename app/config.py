import os
from pathlib import Path

from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]
from pydantic import BaseModel, Field

# 先加载 .env，再读 Settings，保证与 os.environ 一致
_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(_ROOT / ".env")


class Settings(BaseModel):
    # 模型提供方（当前统一走 OpenAI 兼容接口）
    model_provider: str = Field(default=os.getenv("MODEL_PROVIDER", "openai"))
    # 默认模型名称（与 LLM 客户端共用）
    model_name: str = Field(default=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    # 失败重试次数（供后续 LLM/工具重试使用）
    max_retries: int = Field(default=int(os.getenv("MAX_RETRIES", "2")))
    # 子进程/工具通用超时时间（秒）
    tool_timeout_seconds: int = Field(default=int(os.getenv("TOOL_TIMEOUT_SECONDS", "30")))
    # 项目工作目录（解析相对文件路径的基准根）
    workspace_root: str = Field(default=os.getenv("WORKSPACE_ROOT", "."))
    # 知识库根目录，相对于 workspace_root；不存在时忽略
    knowledge_dir: str = Field(default=os.getenv("KNOWLEDGE_DIR", "data/knowledge"))
    # OpenAI 兼容接口（可选，未设置则由 SDK 走默认端点）
    openai_base_url: str | None = Field(
        default=os.getenv("OPENAI_BASE_URL") or None,
    )
    # API 密钥，未设置时 get_llm() 走 fallback
    openai_api_key: str | None = Field(
        default=os.getenv("OPENAI_API_KEY") or None,
    )


# 全局配置对象，供模块直接引用
settings = Settings()

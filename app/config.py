import os

from pydantic import BaseModel, Field


class Settings(BaseModel):
    # 模型提供方（当前统一走 OpenAI 兼容接口）
    model_provider: str = Field(default=os.getenv("MODEL_PROVIDER", "openai"))
    # 默认模型名称
    model_name: str = Field(default=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    # 失败重试次数
    max_retries: int = Field(default=int(os.getenv("MAX_RETRIES", "2")))
    # 工具调用超时时间（秒）
    tool_timeout_seconds: int = Field(default=int(os.getenv("TOOL_TIMEOUT_SECONDS", "30")))
    # 项目工作目录
    workspace_root: str = Field(default=os.getenv("WORKSPACE_ROOT", "."))
    # 知识库目录（RAG 数据来源）
    knowledge_dir: str = Field(default=os.getenv("KNOWLEDGE_DIR", "data/knowledge"))


# 全局配置对象，供模块直接引用
settings = Settings()

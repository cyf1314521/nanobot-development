from pydantic import BaseModel, Field


class Settings(BaseModel):
    model_provider: str = Field(default="mock")
    max_retries: int = Field(default=2)
    tool_timeout_seconds: int = Field(default=30)
    workspace_root: str = Field(default=".")
    knowledge_dir: str = Field(default="data/knowledge")


settings = Settings()

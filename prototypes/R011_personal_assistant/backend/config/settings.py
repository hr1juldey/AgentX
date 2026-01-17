"""Application settings."""

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Personal Assistant"
    version: str = "0.1.0"
    port: int = 8011
    debug: bool = True
    cors_origins: List[str] = ["*"]
    llm_api_url: str = "http://localhost:11434"
    llm_model: str = "gemma3:4b"
    max_tokens: int = 5000

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

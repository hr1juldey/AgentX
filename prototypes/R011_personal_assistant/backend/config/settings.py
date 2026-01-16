"""Application settings."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_name: str = "Personal Assistant"
    version: str = "0.1.0"
    port: int = 8011
    debug: bool = True
    cors_origins: List[str] = ["*"]
    llm_api_url: str = "http://localhost:11434"
    llm_model: str = "llama3.2"
    max_tokens: int = 1000

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

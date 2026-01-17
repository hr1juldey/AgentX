"""Application settings."""

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Analytics Dashboard"
    version: str = "0.1.0"
    port: int = 8012
    debug: bool = True
    cors_origins: List[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

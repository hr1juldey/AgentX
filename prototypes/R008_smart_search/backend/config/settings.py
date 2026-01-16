"""Application settings."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "Smart Search"
    version: str = "0.1.0"
    port: int = 8008
    debug: bool = True
    cors_origins: List[str] = ["*"]

    # Qdrant settings
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "documents"
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    # Search settings
    top_k_results: int = 5
    score_threshold: float = 0.5

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

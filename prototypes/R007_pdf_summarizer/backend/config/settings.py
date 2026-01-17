"""
Configuration settings for PDF Summarizer API.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "PDF Summarizer"
    app_version: str = "1.0.0"
    port: int = 8007
    debug: bool = True

    # API Configuration
    api_prefix: str = "/api/v1"

    # Upload Configuration
    upload_dir: str = "./data/uploads"
    max_file_size: int = 16 * 1024 * 1024  # 16MB
    allowed_extensions: set = {".pdf"}

    # LLM Configuration (Ollama)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"

    # Summary Configuration
    summary_short_max_words: int = 100
    summary_medium_max_words: int = 300
    summary_detailed_max_words: int = 600

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

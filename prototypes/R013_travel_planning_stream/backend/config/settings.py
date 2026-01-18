# =============================================================================
# AGENTX Prototype - Configuration Settings
# =============================================================================
# Pydantic Settings for environment-based configuration
# =============================================================================

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "R013 Travel Planning Stream"
    app_version: str = "0.1.0"
    debug: bool = True

    # Server
    host: str = "0.0.0.0"
    port: int = 8013

    # LLM (Ollama with gemma3:4b)
    llm_model: str = "ollama_chat/gemma3:4b"
    ollama_base_url: str = "http://localhost:11434"
    async_max_workers: int = 4

    # LLM Configuration Mode: "native" or "openai_compatible"
    # native: Uses ollama_chat/* (may have Pydantic warnings)
    # openai_compatible: Uses openai/* with /v1 endpoint (bypasses warnings)
    llm_mode: str = "native"

    # OpenAI-compatible endpoint settings (when llm_mode=openai_compatible)
    ollama_openai_model: str = "openai/gemma3:4b"
    ollama_openai_base_url: str = "http://localhost:11434/v1"
    ollama_openai_api_key: str = "ollama"  # Required by openai adapter

    # Search (SearXNG)
    searxng_url: str = "http://192.168.1.4:8080"

    # CORS
    frontend_url: str = "http://localhost:3000"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export singleton instance
settings = get_settings()

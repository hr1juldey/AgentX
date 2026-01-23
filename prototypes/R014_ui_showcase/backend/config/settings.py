# =============================================================================
# AGENTX R014 - Configuration Settings
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
    app_name: str = "R014 UI Showcase"
    app_version: str = "0.1.0"
    debug: bool = True

    # Server
    host: str = "0.0.0.0"
    port: int = 8014

    # Database
    database_url: str = "sqlite:///./data/database.db"

    # CORS
    frontend_url: str = "http://localhost:3014"

    # =============================================================================
    # LLM Configuration
    # =============================================================================
    # LLM Provider: ollama, openai, anthropic, etc.
    llm_provider: str = "ollama"

    # LLM Model: gemma3:4b, llama3.2, gpt-4o-mini, claude-3-haiku, etc.
    llm_model: str = "gemma3:4b"

    # Ollama Configuration (for provider=ollama)
    ollama_base_url: str = "http://localhost:11434"

    # OpenAI Configuration (for provider=openai)
    openai_api_key: str = ""

    # Anthropic Configuration (for provider=anthropic)
    anthropic_api_key: str = ""

    # DSPy Configuration
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2048

    # =============================================================================
    # Multi-Hop Search Configuration
    # =============================================================================
    # SearXNG Configuration
    searxng_url: str = "http://192.168.1.4:8080"
    searxng_timeout: float = 10.0

    # Multi-Hop Search Parameters
    max_hops: int = 5
    docs_per_hop: int = 5
    stop_threshold: float = 0.85

    # =============================================================================
    # Async Configuration
    # =============================================================================
    # Override auto-detection (useful for testing or forced modes)
    force_async: bool = False
    force_sync: bool = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export singleton instance
settings = get_settings()

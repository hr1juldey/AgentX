# =============================================================================
# R003 Pomodoro Timer - Configuration Settings
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
    app_name: str = "Pomodoro Timer"
    app_version: str = "0.1.0"
    debug: bool = True

    # Server
    host: str = "0.0.0.0"
    port: int = 8003

    # Database
    database_url: str = "sqlite:///./data/database.db"

    # CORS
    frontend_url: str = "http://localhost:3000"

    # Pomodoro Defaults (in seconds)
    default_work_duration: int = 1500  # 25 minutes
    default_break_duration: int = 300  # 5 minutes


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export singleton instance
settings = get_settings()

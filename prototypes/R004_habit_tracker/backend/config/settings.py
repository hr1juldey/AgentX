# =============================================================================
# R004 Habit Tracker - Configuration Settings
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
    app_name: str = "Habit Tracker"
    app_version: str = "0.1.0"
    debug: bool = True

    # Server
    host: str = "0.0.0.0"
    port: int = 8004

    # Database
    database_url: str = "sqlite:///./data/database.db"

    # CORS
    frontend_url: str = "http://localhost:3000"

    # Habit Defaults
    default_target_count: int = 1


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export singleton instance
settings = get_settings()

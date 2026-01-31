"""Core configuration for Real AgentX v0.1.

Uses Pydantic Settings for environment-based configuration.
All values can be overridden via environment variables or .env file.
"""

from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the agentx package directory (parent of core/)
_AGENTX_DIR = Path(__file__).parent.parent.resolve()
_ENV_FILE = _AGENTX_DIR / ".env"


class DatabaseConfig(BaseSettings):
    """Database connection settings."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix="DATABASE__",
    )

    redis_url: str = "redis://localhost:6379/0"
    sqlite_path: Path = Field(default_factory=lambda: Path("data/agentx.db"))
    qdrant_url: str = "http://localhost:6333"


class LLMConfig(BaseSettings):
    """Language model configuration."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix="LLM_",
    )

    provider: str = "ollama"
    model: str = "gemma3:4b"
    api_base: str = "http://localhost:11434"
    temperature: float = 0.7
    max_tokens: int = 4096


class ServerConfig(BaseSettings):
    """Server configuration."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix="SERVER_",
    )

    host: str = "0.0.0.0"
    port: int = 8015
    workers: int = 1
    log_level: str = "info"


class VoiceConfig(BaseSettings):
    """Voice service configuration."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix="VOICE__",
    )

    use_kyutai_external: bool = True
    use_voice_sdk: bool = False
    kyutai_stt_url: str = "ws://localhost:16000/stt"
    kyutai_tts_url: str = "ws://localhost:16000/tts"
    stt_sample_rate: int = 16000
    tts_sample_rate: int = 24000
    vad_threshold: float = 0.5


class SearXNGConfig(BaseSettings):
    """SearXNG search engine configuration."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix="SEARXNG__",
    )

    base_url: str = "http://192.168.1.4:8080"
    timeout: int = 30


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    voice: VoiceConfig = Field(default_factory=VoiceConfig)
    searxng: SearXNGConfig = Field(default_factory=SearXNGConfig)

    app_name: str = "AgentX"
    app_version: str = "0.1.0"
    debug: bool = True


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance.

    Returns:
        Settings: The application settings.
    """
    return settings

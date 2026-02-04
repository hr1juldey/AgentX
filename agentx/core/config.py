"""Core configuration for AGENTX.

Provides Pydantic Settings for all environment variables and configuration.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Global application settings.

    All environment variables are defined here with their defaults.
    """

    # Server
    host: str = "0.0.0.0"
    port: int = 8015

    # LLM
    llm_provider: str = "ollama"
    llm_model: str = "gemma3:4b"
    llm_api_base: str = "http://localhost:11434"

    # Voice (Kyutai)
    voice_kyutai_stt_url: str = "ws://localhost:16000/stt"
    voice_kyutai_tts_url: str = "ws://localhost:16000/tts"
    use_voice_sdk: bool = True

    # Memory (Mem0AI)
    mem0_api_key: str = ""
    mem0_api_url: str = "http://localhost:8000"

    # Retrieval (Qdrant)
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "agentx_memory"

    # LangGraph Checkpoint (Redis)
    redis_url: str = "redis://localhost:6379"

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        case_sensitive = False


# Singleton instance
settings = Settings()

"""Core configuration for AGENTX.

Provides Pydantic Settings for all environment variables and configuration.
"""

from pathlib import Path

from pydantic_settings import BaseSettings

# Project root (3 levels up from this file: agentx/core/config.py → project root)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


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

    # Memory (Mem0AI with local Ollama + Qdrant)
    mem0_qdrant_host: str = "localhost"
    mem0_qdrant_port: int = 6335  # AgentX uses port 6335 to avoid conflicts
    mem0_llm_model: str = "gemma3:4b"
    mem0_embedder_model: str = "mxbai-embed-large:latest"
    mem0_embedding_dims: int = 1024  # mxbai-embed-large uses 1024 dims

    # Retrieval (Qdrant)
    qdrant_host: str = "localhost"
    qdrant_port: int = 6335
    qdrant_url: str = "http://localhost:6335"
    qdrant_collection: str = "agentx_memory"

    # LangGraph Checkpoint (Redis)
    redis_url: str = "redis://localhost:6379"

    class Config:
        """Pydantic configuration."""

        # Try CWD-relative first, fallback to project root absolute path
        env_file = [".env", str(PROJECT_ROOT / ".env")]
        case_sensitive = False
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore undefined env vars (for .env compatibility)


# Singleton instance
settings = Settings()

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

    # LLM (Ollama)
    llm_provider: str = "ollama"
    llm_model: str = "gemma3:4b"
    llm_api_base: str = "http://localhost:11434"
    llm_timeout: int = 600
    llm_temperature: float = 0.7
    llm_max_tokens: int = 16384

    # Voice (Kyutai)
    voice_kyutai_base_url: str = "ws://localhost:16000/api/v1/ws"
    voice_kyutai_stt_url: str = "ws://localhost:16000/api/v1/ws/stt"
    voice_kyutai_tts_url: str = "ws://localhost:16000/api/v1/ws/tts"
    use_voice_sdk: bool = True
    voice_sample_rate: int = 16000
    voice_timeout: float = 1.0
    voice_silence_duration_ms: float = 1500.0

    # Memory (Mem0AI with local Ollama + Qdrant)
    mem0_qdrant_host: str = "localhost"
    mem0_qdrant_port: int = 6335
    mem0_llm_model: str = "gemma3:4b"
    mem0_embedder_model: str = "mxbai-embed-large:latest"
    mem0_embedding_dims: int = 1024

    # Retrieval (Qdrant)
    qdrant_host: str = "localhost"
    qdrant_port: int = 6335
    qdrant_url: str = "http://localhost:6335"
    qdrant_collection: str = "agentx_memory"
    qdrant_dense_dim: int = 1024
    qdrant_colbert_dim: int = 128
    retrieval_prefetch_limit: int = 100
    retrieval_batch_size: int = 100

    # Session
    session_timeout_seconds: int = 300

    # LangGraph Checkpoint (Redis)
    redis_url: str = "redis://localhost:6379"

    class Config:
        """Pydantic configuration."""

        env_file = [".env", str(PROJECT_ROOT / ".env")]
        case_sensitive = False
        env_file_encoding = "utf-8"
        extra = "ignore"


# Singleton instance
settings = Settings()

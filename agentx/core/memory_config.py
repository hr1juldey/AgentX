"""Memory service configuration.

Settings for Qdrant vector store and Mem0AI memory adapter.
From C005 memory-rag change.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the agentx package directory
_AGENTX_DIR = Path(__file__).parent.parent.resolve()
_ENV_FILE = _AGENTX_DIR / ".env"


class MemoryConfig(BaseSettings):
    """Memory service configuration.

    Qdrant settings for vector storage (Tier 2 and Tier 3).
    Mem0AI settings for advanced consolidation.
    """

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix="MEMORY__",
    )

    # Qdrant settings
    qdrant_url: str = "http://localhost:6335"
    tier2_collection_prefix: str = "mem_tier2_"
    tier3_collection_prefix: str = "mem_tier3_"

    # ColBERT embeddings
    colbert_model_name: str = "colbert-ir/colbertv2.0"
    colbert_vector_size: int = 128

    # Temporal RAG settings
    temporal_classification_threshold: float = 0.9
    recent_days_threshold: int = 30

    # Consolidation settings
    consolidation_min_memories: int = 5
    consolidation_max_results: int = 10


# Global settings instance
memory_config = MemoryConfig()


def get_memory_config() -> MemoryConfig:
    """Get the global memory config instance.

    Returns:
        MemoryConfig: The memory configuration.
    """
    return memory_config

"""Qdrant vector store facade for backward compatibility.

This facade maintains backward compatibility with existing imports.
Actual implementation has been moved to the qdrant/ subdirectory.

Deprecated: Import from agentx.infrastructure.database.qdrant instead.
"""

# Re-export all classes for backward compatibility
from agentx.infrastructure.database.qdrant.models import MemoryMetadata
from agentx.infrastructure.database.qdrant.qdrant_vector_store import (
    QdrantVectorStore,
)

__all__ = [
    "MemoryMetadata",
    "QdrantVectorStore",
]

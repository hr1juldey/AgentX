"""Temporal RAG service facade for backward compatibility.

This facade maintains backward compatibility with existing imports.
Actual implementation has been moved to the temporal_rag/ subdirectory.

Deprecated: Import from agentx.application.services.temporal_rag instead.
"""

# Re-export all classes for backward compatibility
from agentx.application.services.temporal_rag.temporal_rag_service import (
    TemporalRAGService,
)

__all__ = ["TemporalRAGService"]

"""Temporal RAG service for Real AgentX v0.1.

This module provides time-aware RAG operations.
Supports temporal filtering, fact invalidation, and multi-hop search.

This module re-exports all classes from split components for backward compatibility.
"""

from agentx.application.services.temporal_rag.temporal_rag_service import (
    TemporalRAGService,
)

__all__ = ["TemporalRAGService"]

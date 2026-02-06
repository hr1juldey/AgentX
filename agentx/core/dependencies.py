"""Core dependency injection for AGENTX.

This module provides a unified import interface for all singleton services.
Individual managers are organized in the managers/ subdirectory.
"""

from __future__ import annotations

# Import all manager functions for backward compatibility
from agentx.application.graphs.presets.conversation_graph import (
    build_conversation_graph,
)
from agentx.core.managers.agent_registry import (
    get_agent_registry,
    register_agent,
)
from agentx.core.managers.dspy import ensure_dspy_configured, get_lm
from agentx.core.managers.mem0_manager import get_mem0_client
from agentx.core.managers.qdrant_manager import (
    get_qdrant_client,
    get_qdrant_collection_manager,
)
from agentx.core.managers.voice_manager import (
    get_voice_gateway,
    get_voice_sdk_adapter,
)
from agentx.core.sessions import get_session_manager

# Singleton conversation graph for all sessions
_chat_graph: object = None


def get_chat_graph() -> object:  # type: ignore[misc]
    """Get or create the singleton conversation graph.

    Returns:
        Compiled StateGraph for conversation
    """
    global _chat_graph
    if _chat_graph is None:
        _chat_graph = build_conversation_graph()
    return _chat_graph


__all__ = [
    # DSPy
    "ensure_dspy_configured",
    "get_lm",
    # Mem0AI
    "get_mem0_client",
    # Qdrant
    "get_qdrant_client",
    "get_qdrant_collection_manager",
    # Voice
    "get_voice_sdk_adapter",
    "get_voice_gateway",
    # Agent registry
    "get_agent_registry",
    "register_agent",
    # Sessions
    "get_session_manager",
    # LangGraph
    "build_conversation_graph",
    "get_chat_graph",
]

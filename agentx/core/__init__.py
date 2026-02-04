"""Core module for AGENTX."""

from agentx.core.config import settings
from agentx.core.dependencies import (
    ensure_dspy_configured,
    get_agent_registry,
    get_mem0_client,
    get_qdrant_client,
    get_session_manager,
    register_agent,
)

__all__ = [
    "settings",
    "ensure_dspy_configured",
    "get_mem0_client",
    "get_qdrant_client",
    "get_agent_registry",
    "register_agent",
    "get_session_manager",
]

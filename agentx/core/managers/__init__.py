"""Core dependency injection managers."""

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
]

"""Core dependency injection for AGENTX."""

import logging
from typing import TYPE_CHECKING, Optional

import dspy

from agentx.core.config import settings

if TYPE_CHECKING:
    from agentx.infrastructure.memory.session_state_manager import SessionStateManager

logger = logging.getLogger(__name__)

_lm: Optional[dspy.LM] = None
_mem0_client: Optional[object] = None
_qdrant_client: Optional[object] = None
_agent_registry: dict = {}
_session_manager: Optional[SessionStateManager] = None


def ensure_dspy_configured() -> None:
    """Configure DSPy globally with Ollama LM."""
    from agentx.infrastructure.external.ollama import check_ollama_health

    global _lm

    if _lm is None:
        check_ollama_health()
        _lm = dspy.LM(
            model=f"ollama_chat/{settings.llm_model}", api_base=settings.llm_api_base
        )
        logger.info(f"DSPy configured with Ollama model: {settings.llm_model}")

    dspy.configure(lm=_lm)


def get_mem0_client() -> object:
    """Get the singleton Mem0AI client."""
    global _mem0_client
    if _mem0_client is None:
        raise NotImplementedError("Mem0AI client not yet implemented")
    return _mem0_client


def get_qdrant_client() -> object:
    """Get the singleton Qdrant client."""
    global _qdrant_client
    if _qdrant_client is None:
        raise NotImplementedError("Qdrant client not yet implemented")
    return _qdrant_client


def get_agent_registry() -> dict:
    """Get the agent registry for graph compilation."""
    return _agent_registry


def register_agent(name: str, agent_class: type) -> None:
    """Register an agent class in the agent registry."""
    _agent_registry[name] = agent_class


def get_session_manager() -> SessionStateManager:
    """Get the singleton SessionStateManager."""
    from agentx.core.sessions import get_session_manager as _get_session_manager

    return _get_session_manager()

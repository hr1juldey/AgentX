"""Core dependency injection for AGENTX.

Provides singleton instances and getter functions for all external dependencies.
"""

from typing import Optional

import dspy

from agentx.core.config import settings

# Global singletons (lazy initialized)
_lm: Optional[dspy.LM] = None
_mem0_client: Optional[object] = None  # Mem0AI client
_qdrant_client: Optional[object] = None
_agent_registry: dict = {}


def ensure_dspy_configured() -> None:
    """Configure DSPy globally with Ollama LM.

    Raises:
        NotImplementedError: If not yet implemented with actual RM configuration.
    """
    global _lm

    if _lm is None:
        _lm = dspy.LM(
            model=f"ollama_chat/{settings.llm_model}",
            api_base=settings.llm_api_base,
        )

    # TODO: Configure RM with Qdrant + ColBERTv2
    # For now, configure without RM
    dspy.configure(lm=_lm)


def get_mem0_client() -> object:
    """Get the singleton Mem0AI client.

    Returns:
        Mem0AI client instance

    Raises:
        NotImplementedError: If not yet implemented.
    """
    global _mem0_client

    if _mem0_client is None:
        raise NotImplementedError("Mem0AI client not yet implemented")

    return _mem0_client


def get_qdrant_client() -> object:
    """Get the singleton Qdrant client.

    Returns:
        Qdrant client instance

    Raises:
        NotImplementedError: If not yet implemented.
    """
    global _qdrant_client

    if _qdrant_client is None:
        raise NotImplementedError("Qdrant client not yet implemented")

    return _qdrant_client


def get_agent_registry() -> dict:
    """Get the agent registry for graph compilation.

    Returns:
        Dictionary mapping agent names to agent classes
    """
    return _agent_registry


def register_agent(name: str, agent_class: type) -> None:
    """Register an agent class in the agent registry.

    Args:
        name: Unique identifier for the agent
        agent_class: Agent class to register
    """
    _agent_registry[name] = agent_class

"""Node Factory - Create DSPy nodes for LangGraph from agent registry."""

from collections.abc import Callable
from typing import Any


def create_dspy_node(agent_class: type, agent_config: dict[str, Any]) -> Callable:
    """Create a LangGraph node from a DSPy agent class.

    Args:
        agent_class: Agent class to instantiate
        agent_config: Configuration for agent initialization

    Returns:
        Callable node function for LangGraph

    Raises:
        NotImplementedError: If not yet implemented
    """
    raise NotImplementedError("create_dspy_node() not yet implemented")

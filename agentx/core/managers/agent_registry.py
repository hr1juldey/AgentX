"""Agent registry for graph compilation."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

_agent_registry: dict = {}


def get_agent_registry() -> dict:
    """Get the agent registry for graph compilation."""
    return _agent_registry


def register_agent(name: str, agent_class: type) -> None:
    """Register an agent class in the agent registry."""
    _agent_registry[name] = agent_class

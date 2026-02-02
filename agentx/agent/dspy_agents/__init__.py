"""DSPy agent implementations for Real AgentX v0.1.

This module provides all agent classes and singleton getter functions.
"""

from agentx.agent.dspy_agents.agents import (
    AnalystAgent,
    DesignerAgent,
    MainDSPyReActAgent,
    MemoryAgent,
)
from agentx.agent.dspy_agents.agent_factory import (
    get_analyst_agent,
    get_designer_agent,
    get_main_agent,
    get_memory_agent,
    reset_agents,
)

__all__ = [
    "MainDSPyReActAgent",
    "AnalystAgent",
    "DesignerAgent",
    "MemoryAgent",
    "get_main_agent",
    "get_analyst_agent",
    "get_designer_agent",
    "get_memory_agent",
    "reset_agents",
]

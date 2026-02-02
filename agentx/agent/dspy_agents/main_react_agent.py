"""Main DSPy ReAct agents facade for backward compatibility.

This facade maintains backward compatibility with existing imports.
Actual implementation has been moved to the agents/ subdirectory.
"""

from agentx.agent.dspy_agents.agent_factory import (
    get_analyst_agent,
    get_designer_agent,
    get_main_agent,
    get_memory_agent,
    reset_agents,
)
from agentx.agent.dspy_agents.agents import (
    AnalystAgent,
    DesignerAgent,
    MainDSPyReActAgent,
    MemoryAgent,
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

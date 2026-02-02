"""Agent factory and singleton management.

Provides lazy-loaded agent instances with DSPy configuration.
"""

from agentx.core.dependencies import ensure_dspy_configured
from agentx.agent.dspy_agents.agents.analyst import AnalystAgent
from agentx.agent.dspy_agents.agents.designer import DesignerAgent
from agentx.agent.dspy_agents.agents.main import MainDSPyReActAgent
from agentx.agent.dspy_agents.agents.memory import MemoryAgent


# Global agent instances (lazy-loaded)
_main_agent: MainDSPyReActAgent | None = None
_analyst_agent: AnalystAgent | None = None
_designer_agent: DesignerAgent | None = None
_memory_agent: MemoryAgent | None = None


def get_main_agent() -> MainDSPyReActAgent:
    """Get the main ReAct agent singleton.

    Returns:
        MainDSPyReActAgent: The main agent instance.
    """
    ensure_dspy_configured()
    global _main_agent
    if _main_agent is None:
        _main_agent = MainDSPyReActAgent()
    return _main_agent


def get_analyst_agent() -> AnalystAgent:
    """Get the analyst agent singleton.

    Returns:
        AnalystAgent: The analyst agent instance.
    """
    ensure_dspy_configured()
    global _analyst_agent
    if _analyst_agent is None:
        _analyst_agent = AnalystAgent()
    return _analyst_agent


def get_designer_agent() -> DesignerAgent:
    """Get the designer agent singleton.

    Returns:
        DesignerAgent: The designer agent instance.
    """
    ensure_dspy_configured()
    global _designer_agent
    if _designer_agent is None:
        _designer_agent = DesignerAgent()
    return _designer_agent


def get_memory_agent() -> MemoryAgent:
    """Get the memory agent singleton.

    Returns:
        MemoryAgent: The memory agent instance.
    """
    ensure_dspy_configured()
    global _memory_agent
    if _memory_agent is None:
        _memory_agent = MemoryAgent()
    return _memory_agent


def reset_agents() -> None:
    """Reset all agent singletons.

    Useful for testing or clearing state.
    """
    global _main_agent, _analyst_agent, _designer_agent, _memory_agent
    _main_agent = None
    _analyst_agent = None
    _designer_agent = None
    _memory_agent = None

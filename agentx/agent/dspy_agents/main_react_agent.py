"""Main DSPy ReAct agent for Real AgentX v0.1.

Implements the primary agent using DSPy ReAct pattern.
Following DSPy tutorial patterns from /home/riju279/Downloads/dspy-main/dspy-main/docs/
"""

import dspy
from dspy import Example

from agentx.agent.dspy_signatures.main_signatures import MainAgentSignature
from agentx.agent.tools.main_tools import AVAILABLE_TOOLS
from agentx.core.dependencies import ensure_dspy_configured


class MainDSPyReActAgent(dspy.ReAct):
    """Main ReAct agent for query processing.

    Uses DSPy ReAct pattern for multi-step reasoning with tools.
    """

    def __init__(self) -> None:
        """Initialize the main ReAct agent with tools."""
        super().__init__(
            signature=MainAgentSignature,
            tools=AVAILABLE_TOOLS,
            max_iters=5,  # Maximum reasoning steps
        )

    def forward(self, query: str, context: str = "") -> Example:
        """Process a user query.

        Args:
            query: User's question or request.
            context: Optional context from memory or tools.

        Returns:
            Example: Agent response with reasoning.
        """
        # Call parent forward method
        result = super().forward(query=query, context=context)

        return result


class AnalystAgent(dspy.Module):
    """Analyst agent for query understanding and intent extraction."""

    def __init__(self) -> None:
        """Initialize the analyst agent."""
        super().__init__()
        self.analyze = dspy.Predict(
            "agentx/agent/dspy_signatures/main_signatures.py::AnalystSignature"
        )

    def forward(self, query: str) -> dict:
        """Analyze user query to extract intent and entities.

        Args:
            query: User's question or request.

        Returns:
            dict: Analysis results with intent, entities, tool needs.
        """
        result = self.analyze(query=query)
        return {
            "intent": result.intent,
            "entities": result.entities,
            "tool_needed": result.tool_needed,
            "tool_name": result.tool_name,
        }


class DesignerAgent(dspy.Module):
    """Designer agent for UI widget selection.

    Server-driven UI pattern from C007 - selects widgets with state awareness.
    """

    def __init__(self) -> None:
        """Initialize the designer agent."""
        super().__init__()
        self.design = dspy.Predict(
            "agentx/agent/dspy_signatures/main_signatures.py::DesignerSignature"
        )

    def forward(self, query: str, response: str, existing_widgets: list[str]) -> dict:
        """Select appropriate UI widget based on query and context.

        Args:
            query: User's question or request.
            response: Agent's response content.
            existing_widgets: List of already shown widget types.

        Returns:
            dict: Widget recommendation with type and props.
        """
        result = self.design(
            query=query, response=response, existing_widgets=existing_widgets
        )
        return {
            "recommended_widget": result.recommended_widget,
            "widget_props": result.widget_props,
        }


class MemoryAgent(dspy.Module):
    """Memory agent for RAG operations.

    Retrieves relevant context from episodic, semantic, and procedural memory.
    """

    def __init__(self) -> None:
        """Initialize the memory agent."""
        super().__init__()
        self.retrieve = dspy.Predict(
            "agentx/agent/dspy_signatures/main_signatures.py::MemorySignature"
        )

    def forward(self, query: str, session_id: str) -> dict:
        """Retrieve relevant context from memory.

        Args:
            query: User's question or request.
            session_id: Current session identifier.

        Returns:
            dict: Retrieved context with source references.
        """
        result = self.retrieve(query=query, session_id=session_id)
        return {
            "context": result.context,
            "sources": result.sources,
        }


# Global agent instances (lazy-loaded in dependencies.py)
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

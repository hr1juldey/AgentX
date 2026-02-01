"""Main DSPy ReAct agent for Real AgentX v0.1.

Implements the primary agent using DSPy ReAct pattern.
Following DSPy tutorial patterns from /home/riju279/Downloads/dspy-main/dspy-main/docs/
"""

import dspy

from agentx.agent.dspy_signatures.main_signatures import (
    MainAgentSignature,
    AnalystSignature,
    DesignerSignature,
    MemorySignature,
)
from agentx.agent.tools.main_tools import AVAILABLE_TOOLS
from agentx.core.dependencies import ensure_dspy_configured


class MainDSPyReActAgent(dspy.Module):
    """Main ReAct agent for query processing.

    Uses DSPy ReAct pattern for multi-step reasoning with tools.
    NOTE: Extends dspy.Module and uses dspy.ReAct as a sub-module,
    following the pattern from DSPy tutorials (e.g., mem0_react_agent).
    """

    def __init__(self) -> None:
        """Initialize the main ReAct agent with tools."""
        super().__init__()
        # ReAct is used as a sub-module, not inherited directly
        self.react = dspy.ReAct(
            signature=MainAgentSignature,
            tools=AVAILABLE_TOOLS,  # type: ignore[arg-type]  # list[Tool] is compatible with list[Callable]
            max_iters=5,  # Maximum reasoning steps
        )

    def forward(self, **kwargs) -> dspy.Prediction:
        """Process a user query.

        Args:
            **kwargs: Keyword arguments matching MainAgentSignature inputs
                     (query: str, context: str = "")

        Returns:
            dspy.Prediction: Agent response with reasoning.
        """
        # Delegate to the ReAct sub-module
        # type: ignore[bad-return]  # @with_callbacks confuses pyrefly; actual return is Prediction
        return self.react(**kwargs)


class AnalystAgent(dspy.Module):
    """Analyst agent for query understanding and intent extraction."""

    def __init__(self) -> None:
        """Initialize the analyst agent."""
        super().__init__()
        self.analyze = dspy.Predict(AnalystSignature)

    def forward(self, query: str) -> dspy.Prediction:
        """Analyze user query to extract intent and entities.

        Args:
            query: User's question or request.

        Returns:
            dspy.Prediction: Analysis results with intent, entities, tool needs.
        """
        result = self.analyze(query=query)
        return dspy.Prediction(
            intent=result.intent,  # type: ignore[attr-defined]  # Pyrefly thinks result is Coroutine
            entities=result.entities,  # type: ignore[attr-defined]
            tool_needed=result.tool_needed,  # type: ignore[attr-defined]
            tool_name=result.tool_name,  # type: ignore[attr-defined]
        )


class DesignerAgent(dspy.Module):
    """Designer agent for UI widget selection.

    Server-driven UI pattern from C007 - selects widgets with state awareness.
    """

    def __init__(self) -> None:
        """Initialize the designer agent."""
        super().__init__()
        self.design = dspy.Predict(DesignerSignature)

    def forward(
        self, query: str, response: str, existing_widgets: list[str]
    ) -> dspy.Prediction:
        """Select appropriate UI widget based on query and context.

        Args:
            query: User's question or request.
            response: Agent's response content.
            existing_widgets: List of already shown widget types.

        Returns:
            dspy.Prediction: Widget recommendation with type and props.
        """
        result = self.design(
            query=query, response=response, existing_widgets=existing_widgets
        )
        return dspy.Prediction(
            recommended_widget=result.recommended_widget,  # type: ignore[attr-defined]  # Pyrefly thinks result is Coroutine
            widget_props=result.widget_props,  # type: ignore[attr-defined]
        )


class MemoryAgent(dspy.Module):
    """Memory agent for RAG operations.

    Retrieves relevant context from episodic, semantic, and procedural memory.
    """

    def __init__(self) -> None:
        """Initialize the memory agent."""
        super().__init__()
        self.retrieve = dspy.Predict(MemorySignature)

    def forward(self, query: str, session_id: str) -> dspy.Prediction:
        """Retrieve relevant context from memory.

        Args:
            query: User's question or request.
            session_id: Current session identifier.

        Returns:
            dspy.Prediction: Retrieved context with source references.
        """
        result = self.retrieve(query=query, session_id=session_id)
        return dspy.Prediction(
            context=result.context,  # type: ignore[attr-defined]  # Pyrefly thinks result is Coroutine
            sources=result.sources,  # type: ignore[attr-defined]
        )


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

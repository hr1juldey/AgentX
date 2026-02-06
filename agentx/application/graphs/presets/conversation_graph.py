"""Conversation Graph preset - multi-node text chat processing.

Following CLAUDE_POLICY.md:
- Absolute imports only (no relative imports)
- File size < 100 lines executable code
- Follows folder structure conventions spec
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from agentx.application.graphs.nodes import (
    conversation_agent_node,
    format_output_node,
    validate_input_node,
)
from agentx.application.graphs.state import ChatState


def build_conversation_graph() -> object:  # type: ignore[misc]
    """Build preset graph for conversation flow.

    Graph structure:
    START → validate_input → conversation_agent → format_output → END

    Returns:
        Compiled StateGraph for conversation with MemorySaver checkpointer
    """
    graph = StateGraph(ChatState)  # type: ignore[misc]

    graph.add_node("validate_input", validate_input_node)  # type: ignore[call-arg]
    graph.add_node("conversation_agent", conversation_agent_node)  # type: ignore[call-arg]
    graph.add_node("format_output", format_output_node)  # type: ignore[call-arg]

    graph.add_edge(START, "validate_input")
    graph.add_edge("validate_input", "conversation_agent")
    graph.add_edge("conversation_agent", "format_output")
    graph.add_edge("format_output", END)

    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)


__all__ = ["build_conversation_graph"]

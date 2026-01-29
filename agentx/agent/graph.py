"""LangGraph graph definition for Real AgentX v0.1.

StateGraph with 8 nodes implementing the complete 7-pipeline agent sequence.
Following LangGraph patterns from docs.langchain.com/langsmith/generative-ui-react

**R014 Migration**: Callback pattern replaced with state-based UI tracking.
"""

from typing import Literal, cast

from langgraph.graph import StateGraph, END

from agentx.agent.state import AgentState
from agentx.agent.nodes.analyst import analyst_node
from agentx.agent.nodes.contextualizer import contextualizer_node
from agentx.agent.nodes.designer import designer_node
from agentx.agent.nodes.presenter import presenter_node
from agentx.agent.nodes.researcher import researcher_node
from agentx.agent.nodes.sequencer import sequencer_node
from agentx.agent.nodes.widget_selector import widget_selector_node


def _should_continue_research(
    state: AgentState,
) -> Literal["continue_research", "finalize"]:
    """Conditional edge: Decide whether to continue research or finalize.

    Checks the quality assessment from analyst Pass 2 to determine
    if more research is needed.

    Args:
        state: Current agent state

    Returns:
        Next action: continue_research or finalize
    """
    # Get quality assessment from analyst Pass 2
    messages = state.get("messages", [])
    for msg in reversed(messages):
        if hasattr(msg, "content") and isinstance(msg.content, str):
            content = msg.content.lower()
            # Check if analyst Pass 2 indicated need for more research
            if (
                "needs more research: true" in content
                or "needs more research: yes" in content
            ):
                return "continue_research"
            break

    # Default: finalize
    return "finalize"


def create_graph() -> StateGraph:
    """Create the complete agent StateGraph with all 8 nodes.

    The graph implements the R014 7-pipeline sequence:
    1. analyst_p1: Analyze query (extract terms, insights, goals)
    2. researcher: Web search and data extraction
    3. contextualizer: Rerank, filter, and inject context
    4. analyst_p2: Judge data quality (may loop back to researcher)
    5. designer: STATE AWARE widget selection (checks state.ui)
    6. widget_selector: Hybrid rule + LLM widget matching
    7. sequencer: Order and pace widgets (staggered delivery)
    8. presenter: Final presentation with QA

    Returns:
        StateGraph: The configured agent graph.
    """
    # Create the graph with AgentState
    graph = StateGraph(AgentState)

    # Add all 8 nodes
    graph.add_node(cast(str, "analyst_p1"), analyst_node)  # type: ignore[arg-type]
    graph.add_node(cast(str, "researcher"), researcher_node)  # type: ignore[arg-type]
    graph.add_node(cast(str, "contextualizer"), contextualizer_node)  # type: ignore[arg-type]
    graph.add_node(cast(str, "analyst_p2"), analyst_node)  # type: ignore[arg-type]
    graph.add_node(cast(str, "designer"), designer_node)  # type: ignore[arg-type]
    graph.add_node(cast(str, "widget_selector"), widget_selector_node)  # type: ignore[arg-type]
    graph.add_node(cast(str, "sequencer"), sequencer_node)  # type: ignore[arg-type]
    graph.add_node(cast(str, "presenter"), presenter_node)  # type: ignore[arg-type]

    # Set entry point
    graph.set_entry_point("analyst_p1")

    # Add edges for the main pipeline flow
    graph.add_edge("analyst_p1", "researcher")
    graph.add_edge("researcher", "contextualizer")
    graph.add_edge("contextualizer", "analyst_p2")

    # Conditional edge: Check if more research is needed
    graph.add_conditional_edges(
        "analyst_p2",
        _should_continue_research,
        {
            "continue_research": "researcher",
            "finalize": "designer",
        },
    )

    # Complete the pipeline
    graph.add_edge("designer", "widget_selector")
    graph.add_edge("widget_selector", "sequencer")
    graph.add_edge("sequencer", "presenter")
    graph.add_edge("presenter", END)

    # Compile the graph
    return graph


# Global graph instance
_graph: StateGraph | None = None


def get_graph() -> StateGraph:
    """Get the agent graph singleton.

    Returns:
        StateGraph: The agent graph instance.
    """
    global _graph
    if _graph is None:
        _graph = create_graph()
    return _graph


def reset_graph() -> None:
    """Reset the graph singleton.

    Useful for testing.
    """
    global _graph
    _graph = None

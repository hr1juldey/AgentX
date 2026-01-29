"""LangGraph graph definition for Real AgentX v0.1.

StateGraph with nodes for analyst, designer, and execution.
Following LangGraph patterns from docs.langchain.com/langsmith/generative-ui-react
"""

from langgraph.graph import StateGraph, END

from agentx.agent.state import AgentState
from agentx.agent.nodes.analyst import analyst_node
from agentx.agent.nodes.designer import designer_node
from agentx.agent.nodes.executor import executor_node


def create_graph() -> StateGraph:
    """Create the agent StateGraph.

    The graph orchestrates the agent workflow:
    1. analyst: Analyze query to extract intent and entities
    2. designer: Select UI components based on state (state awareness!)
    3. executor: Execute tools and generate response

    Returns:
        StateGraph: The configured agent graph.
    """

    # Create the graph with AgentState
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("analyst", analyst_node)
    graph.add_node("designer", designer_node)
    graph.add_node("executor", executor_node)

    # Set entry point
    graph.set_entry_point("analyst")

    # Add edges
    graph.add_edge("analyst", "designer")
    graph.add_edge("designer", "executor")
    graph.add_edge("executor", END)

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

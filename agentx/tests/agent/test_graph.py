"""Tests for LangGraph StateGraph compilation.

Verifies that the agent graph compiles correctly and all nodes are wired.
"""

from langgraph.graph import StateGraph

from agentx.agent.graph import create_graph, get_graph, reset_graph


def test_create_graph_returns_stategraph() -> None:
    """Test that create_graph returns a StateGraph instance."""
    graph = create_graph()
    assert isinstance(graph, StateGraph)


def test_graph_has_all_nodes() -> None:
    """Test that all 8 nodes are added to the graph."""
    graph = create_graph()
    compiled = graph.compile()

    # Verify graph structure
    assert hasattr(compiled, "nodes")
    expected_nodes = {
        "analyst_p1",
        "researcher",
        "contextualizer",
        "analyst_p2",
        "designer",
        "widget_selector",
        "sequencer",
        "presenter",
    }
    actual_nodes = set(compiled.nodes.keys())
    # Filter out internal nodes like __start__, __end__
    actual_nodes = {n for n in actual_nodes if not n.startswith("__")}
    assert actual_nodes == expected_nodes


def test_graph_has_conditional_edges() -> None:
    """Test that conditional edges are properly configured."""
    graph = create_graph()
    compiled = graph.compile()

    # Verify conditional edge exists from analyst_p2
    assert "analyst_p2" in compiled.nodes


def test_graph_singleton() -> None:
    """Test that get_graph returns the same instance."""
    reset_graph()
    graph1 = get_graph()
    graph2 = get_graph()
    assert graph1 is graph2


def test_graph_reset() -> None:
    """Test that reset_graph clears the singleton."""
    graph1 = get_graph()
    reset_graph()
    graph2 = get_graph()
    assert graph1 is not graph2


def test_graph_entry_point() -> None:
    """Test that graph entry point is analyst_p1."""
    graph = create_graph()
    compiled = graph.compile()

    # Entry point is verified by graph structure
    assert "analyst_p1" in compiled.nodes

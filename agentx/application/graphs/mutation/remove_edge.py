"""Remove edge mutation operation."""

from langgraph.graph import StateGraph


def remove_edge(graph: StateGraph, source: str, target: str) -> StateGraph:
    """Remove an edge from the running graph.

    Args:
        graph: The StateGraph to modify
        source: Source node identifier
        target: Target node identifier

    Returns:
        Modified StateGraph

    Raises:
        NotImplementedError: If not yet implemented
    """
    raise NotImplementedError("remove_edge() not yet implemented")

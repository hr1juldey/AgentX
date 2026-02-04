"""Add node mutation operation."""

from langgraph.graph import StateGraph


def add_node(graph: StateGraph, node_id: str, agent: str) -> StateGraph:
    """Add a new node to the running graph.

    Args:
        graph: The StateGraph to modify
        node_id: New node identifier
        agent: Agent class or name to use for the node

    Returns:
        Modified StateGraph

    Raises:
        NotImplementedError: If not yet implemented
    """
    raise NotImplementedError("add_node() not yet implemented")

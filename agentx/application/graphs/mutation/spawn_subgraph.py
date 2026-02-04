"""Spawn subgraph mutation operation."""

from langgraph.graph import StateGraph


def spawn_subgraph(parent: StateGraph, entry_point: str) -> StateGraph:
    """Create isolated subgraph from parent graph.

    Args:
        parent: Parent StateGraph
        entry_point: Entry point node in parent

    Returns:
        New isolated subgraph

    Raises:
        NotImplementedError: If not yet implemented
    """
    raise NotImplementedError("spawn_subgraph() not yet implemented")

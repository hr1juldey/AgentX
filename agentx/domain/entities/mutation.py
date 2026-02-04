"""Mutation entity for graph mutation operations."""

from dataclasses import dataclass


@dataclass
class Mutation:
    """Represents a graph mutation operation.

    Attributes:
        type: Mutation type (add_node, remove_edge, modify_condition, spawn_subgraph)
        target: Target node/edge identifier
        params: Mutation parameters
    """

    type: str
    target: str
    params: dict

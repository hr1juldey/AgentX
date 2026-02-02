"""Dynamic Agent Graph with state-driven routing.

This module compiles the StateGraph with all nodes, edges, and routing logic.
The graph dynamically creates workers via Send API based on execution plans.

IMPORTANT: Use get_dynamic_agent() to obtain the compiled graph.
The graph uses lazy compilation - it's only compiled when first requested
to ensure Redis connections are available from FastAPI lifespan.
"""

from agentx.agent.graph.dynamic_agent_graph import (
    build_dynamic_agent_graph,
    get_dynamic_agent,
    get_graph,
)

__all__ = [
    "build_dynamic_agent_graph",
    "get_dynamic_agent",
    "get_graph",
]

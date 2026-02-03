"""Dynamic Agent Graph with state-driven routing.

This module compiles the StateGraph with all nodes, edges, and routing logic.
The graph dynamically creates workers via Send API based on execution plans.

Graph compilation is lazy - the graph is only compiled when first requested,
ensuring Redis connections are available from FastAPI lifespan.
"""

from typing import Any

from langgraph.graph import StateGraph  # type: ignore[import]

from agentx.agent.graph.graph_builder_helpers import register_edges, register_nodes
from agentx.domain.models.graph_state import AgentState
from agentx.infrastructure.memory.checkpointer_config import get_checkpointer
from agentx.infrastructure.memory.langgraph_store_adapter import get_store


def build_dynamic_agent_graph() -> StateGraph:
    """Build the dynamic agent graph.

    The graph:
    1. Routes by input path (STT vs TEXT)
    2. Generates execution plan
    3. Checks cache for prior research
    4. Routes by plan (direct answer vs create workers)
    5. Assigns dynamic workers via Send API
    6. Executes research workers
    7. Evaluates progress (continue or finalize)
    8. Synthesizes response with streaming

    Returns:
        StateGraph: Compiled graph ready for invocation
    """
    builder = StateGraph(AgentState)

    # Register all nodes
    register_nodes(builder)

    # Register all edges
    register_edges(builder)

    return builder


# Module-level cache for compiled graph (lazy compilation)
# Type: Any because CompiledStateGraph is not directly importable from langgraph
_dynamic_agent_graph_instance: Any = None


def get_dynamic_agent():
    """Get compiled dynamic agent with memory.

    Compiles the graph with both checkpointer (graph memory)
    and store (agent memory) for full functionality.

    Uses lazy compilation - only compiles when first requested
    to ensure Redis connections are available from lifespan.

    Returns:
        Compiled graph with memory support

    Raises:
        RuntimeError: If Redis connections not initialized
    """
    global _dynamic_agent_graph_instance
    if _dynamic_agent_graph_instance is None:
        builder = build_dynamic_agent_graph()

        # Compile with BOTH memory types
        _dynamic_agent_graph_instance = builder.compile(
            checkpointer=get_checkpointer(),  # Graph memory (procedural)
            store=get_store(),  # Agent memory (episodic)
        )

    return _dynamic_agent_graph_instance


def get_graph() -> StateGraph:
    """Get the graph builder for compilation.

    Returns:
        StateGraph: The graph builder
    """
    return build_dynamic_agent_graph()

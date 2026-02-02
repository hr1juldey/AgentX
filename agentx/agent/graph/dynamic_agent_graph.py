"""Dynamic Agent Graph with state-driven routing.

This module compiles the StateGraph with all nodes, edges, and routing logic.
The graph dynamically creates workers via Send API based on execution plans.
"""

from langgraph.graph import StateGraph, START, END  # type: ignore[import]

from agentx.agent.nodes.cache_lookup import cache_lookup_node
from agentx.agent.nodes.evaluator import evaluator_node, should_continue_research
from agentx.agent.nodes.progress_tracker import progress_tracker_node
from agentx.agent.nodes.query_planner import query_planner_node
from agentx.agent.nodes.research_worker import research_worker_node
from agentx.agent.nodes.routing import assign_workers, route_by_plan
from agentx.agent.nodes.stt_preprocessor import (
    route_by_input_path,
    stt_preprocessor_node,
)
from agentx.agent.nodes.synthesizer import direct_answer_node, synthesizer_node
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

    # Add nodes
    builder.add_node("stt_preprocessor", stt_preprocessor_node)  # type: ignore[arg-type]
    builder.add_node("query_planner", query_planner_node)  # type: ignore[arg-type]
    builder.add_node("cache_lookup", cache_lookup_node)  # type: ignore[arg-type]
    builder.add_node("direct_answer", direct_answer_node)  # type: ignore[arg-type]
    builder.add_node("research_worker", research_worker_node)  # type: ignore[arg-type]
    builder.add_node("evaluator", evaluator_node)  # type: ignore[arg-type]
    builder.add_node("synthesizer", synthesizer_node)  # type: ignore[arg-type]
    builder.add_node("progress_tracker", progress_tracker_node)  # type: ignore[arg-type]

    # Entry point: route by input path
    builder.add_conditional_edges(
        START,
        route_by_input_path,
        {
            "stt_preprocessor": "stt_preprocessor",
            "query_planner": "query_planner",
        },
    )

    # After STT preprocessing, go to query planner
    builder.add_edge("stt_preprocessor", "query_planner")

    # After query planning, check cache
    builder.add_edge("query_planner", "cache_lookup")

    # Route by plan: direct answer or create workers
    builder.add_conditional_edges(
        "cache_lookup",
        route_by_plan,
        {
            "direct_answer": "direct_answer",
            "create_workers": "assign_workers",
        },
    )

    # Send API: create dynamic workers
    builder.add_conditional_edges(
        "assign_workers",
        assign_workers,  # Returns list[Send]
        ["research_worker"],  # Dynamic target
    )

    # After worker completes, evaluate progress
    builder.add_edge("research_worker", "evaluator")

    # Evaluator decides: continue, add tasks, or finalize
    builder.add_conditional_edges(
        "evaluator",
        should_continue_research,
        {
            "continue": "assign_workers",
            "add_tasks": "assign_workers",
            "finalize": "synthesizer",
        },
    )

    # Synthesizer generates final response
    builder.add_edge("synthesizer", END)
    builder.add_edge("direct_answer", END)

    return builder


def get_dynamic_agent():
    """Get compiled dynamic agent with memory.

    Compiles the graph with both checkpointer (graph memory)
    and store (agent memory) for full functionality.

    Returns:
        Compiled graph with memory support
    """
    builder = build_dynamic_agent_graph()

    # Compile with BOTH memory types
    graph = builder.compile(
        checkpointer=get_checkpointer(),  # Graph memory (procedural)
        store=get_store(),  # Agent memory (episodic)
    )

    return graph


# Main graph instance
dynamic_agent_graph = get_dynamic_agent()

"""Graph builder helper functions for dynamic agent graph.

Provides helper functions to register nodes and edges with the StateGraph.
"""

from langgraph.graph import END, START, StateGraph  # type: ignore[import]

from agentx.agent.nodes.cache_lookup import cache_lookup_node
from agentx.agent.nodes.evaluator import evaluator_node, should_continue_research
from agentx.agent.nodes.progress_tracker import progress_tracker_node
from agentx.agent.nodes.query_planner import query_planner_node
from agentx.agent.nodes.research_worker import research_worker_node
from agentx.agent.nodes.routing import (
    _create_worker_sends,
    assign_workers_node,
    route_by_plan,
)
from agentx.agent.nodes.stt_preprocessor import (
    route_by_input_path as stt_route_by_input_path,
    stt_preprocessor_node,
)
from agentx.agent.nodes.synthesizer import direct_answer_node, synthesizer_node


def register_nodes(builder: StateGraph) -> None:
    """Register all nodes with the StateGraph builder.

    Args:
        builder: StateGraph builder instance
    """
    builder.add_node("stt_preprocessor", stt_preprocessor_node)  # type: ignore[arg-type]
    builder.add_node("query_planner", query_planner_node)  # type: ignore[arg-type]
    builder.add_node("cache_lookup", cache_lookup_node)  # type: ignore[arg-type]
    builder.add_node("assign_workers", assign_workers_node)  # type: ignore[arg-type]
    builder.add_node("direct_answer", direct_answer_node)  # type: ignore[arg-type]
    builder.add_node("research_worker", research_worker_node)  # type: ignore[arg-type]
    builder.add_node("evaluator", evaluator_node)  # type: ignore[arg-type]
    builder.add_node("synthesizer", synthesizer_node)  # type: ignore[arg-type]
    builder.add_node("progress_tracker", progress_tracker_node)  # type: ignore[arg-type]


def register_edges(builder: StateGraph) -> None:
    """Register all edges with the StateGraph builder.

    Args:
        builder: StateGraph builder instance
    """
    # Entry point: route by input path
    builder.add_conditional_edges(
        START,
        stt_route_by_input_path,
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
        _create_worker_sends,  # Returns list[Send]
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


__all__ = [
    "register_nodes",
    "register_edges",
]

"""Routing nodes for the dynamic agent graph.

This module contains the routing functions that determine execution flow
based on the execution plan and Send API for dynamic worker creation.
"""

from typing import Any

from langgraph.types import Send  # type: ignore[import]

from agentx.domain.models.graph_state import AgentState
from agentx.domain.models.routing import RoutingPath


def route_by_plan(state: AgentState) -> RoutingPath:
    """Route based on execution plan.

    Key insight: Zero tasks → direct answer (no Send API needed).
    This avoids unnecessary worker creation for simple queries.

    Args:
        state: Current agent state

    Returns:
        RoutingPath: Either "direct_answer" or "create_workers"
    """
    plan = state["execution_plan"]

    # Filter out cached tasks (already loaded from Store)
    uncached_tasks = [t for t in plan.research_tasks if not t.cached]

    if len(uncached_tasks) == 0:
        return RoutingPath.DIRECT_ANSWER
    else:
        return RoutingPath.CREATE_WORKERS


def _create_worker_sends(state: AgentState) -> list[Send]:
    """Create DYNAMIC workers via Send API based on execution plan.

    This is NOT a fixed pipeline. Workers are created DYNAMICALLY based on:
    - Plan's task list
    - Dependencies (respect task.dependencies)
    - Already-visited tasks (avoid cycles)

    Args:
        state: Current agent state

    Returns:
        list[Send]: Dynamic worker invocations
    """
    plan = state["execution_plan"]
    visited = set(state.get("visited_tasks", []))

    # Find ready tasks: deps satisfied, not visited, not cached
    ready_tasks = [
        t
        for t in plan.research_tasks
        if not t.cached
        and all(dep in visited for dep in t.dependencies)
        and t.task_id not in visited
    ]

    # DYNAMIC worker creation - one Send per ready task
    return [
        Send("research_worker", {"current_task": t.model_dump()}) for t in ready_tasks
    ]


def assign_workers_node(state: AgentState) -> dict[str, Any]:
    """Node that triggers worker creation - returns state updates for LangGraph.

    The actual Send objects are created by the conditional edge routing function
    (_create_worker_sends) that runs after this node completes.

    Args:
        state: Current agent state

    Returns:
        dict: Empty state updates (routing is handled by conditional edge)
    """
    # The conditional edge will call _create_worker_sends to generate Send objects
    # This node just needs to complete successfully
    return {}


def should_continue_routing(state: AgentState) -> str:
    """Route after evaluator decision.

    Args:
        state: Current agent state

    Returns:
        str: "continue", "add_tasks", or "finalize"
    """
    decision = state.get("continuation_decision")
    if not decision:
        return "finalize"

    # Max iterations safety check
    max_iterations = 5
    iteration = state.get("current_iteration", 0)

    if iteration >= max_iterations:
        return "finalize"

    # Route based on decision action
    action = decision.action  # type: ignore[attr-defined]
    if action == "continue_research":
        return "continue"
    elif action == "add_tasks":
        return "add_tasks"
    else:
        return "finalize"

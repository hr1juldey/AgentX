"""Cache lookup node for the dynamic agent graph.

This node checks agent memory (Store) for cached research results
before executing new tasks, enabling fast responses for repeated queries.
"""

import hashlib

from agentx.domain.models.graph_state import AgentState
from agentx.domain.models.query_plan import ExecutionPlan
from agentx.infrastructure.memory.langgraph_store_adapter import (
    EpisodicMemoryStore,
    get_store,
)


async def cache_lookup_node(state: AgentState) -> dict:
    """Check agent memory for cached research results.

    This node searches for cached research results by query hash.
    Cached results are loaded directly without re-executing tasks.

    Args:
        state: Current agent state with execution_plan

    Returns:
        dict: Updated state with cached task results and modified plan
    """
    plan: ExecutionPlan = state["execution_plan"]
    user_id = state["user_id"]
    query = plan.query

    # Initialize memory store
    store = get_store()
    memory_store = EpisodicMemoryStore(store)

    # Search for cached memories
    memories = await memory_store.search_research_memories(
        query=query,
        user_id=user_id,
        limit=5,
    )

    # Map cached results to tasks
    task_results: dict[str, str] = {}
    cached_task_ids: set[str] = set()

    for memory in memories:
        # Find matching task by query similarity
        for task in plan.research_tasks:
            query_hash = hashlib.sha256(task.query.lower().encode()).hexdigest()

            # Check if this memory matches the task
            if (
                memory.query_hash == query_hash
                or task.query.lower() in memory.result.lower()
            ):
                task_results[task.task_id] = memory.result
                cached_task_ids.add(task.task_id)
                break

    # Update plan to mark cached tasks
    updated_tasks = []
    for task in plan.research_tasks:
        if task.task_id in cached_task_ids:
            # Mark as cached and load result
            task.cached = True
            task.result = task_results.get(task.task_id, "")
        updated_tasks.append(task)

    # Load cached findings
    research_findings: list[str] = []
    research_sources: list[str] = []

    for memory in memories:
        if memory.result:
            research_findings.append(memory.summary)
            research_sources.append(f"memory:{memory.memory_id}")

    return {
        "execution_plan": plan.model_copy(update={"research_tasks": updated_tasks}),
        "task_results": task_results,
        "research_findings": research_findings,
        "research_sources": research_sources,
        "execution_path": ["cache_lookup"],
    }

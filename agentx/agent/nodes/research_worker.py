"""Research worker node for the dynamic agent graph.

This node executes individual research tasks created by the Send API.
It's invoked dynamically for each ready task in the execution plan.
"""

from agentx.domain.models.graph_state import AgentState
from agentx.domain.models.query_plan import ResearchTask, TaskType


async def research_worker_node(state: AgentState) -> dict:
    """Execute a single research task.

    This node is invoked dynamically by the Send API for each
    ready task in the execution plan. It executes the task and
    returns the result.

    Args:
        state: Current agent state with current_task in metadata

    Returns:
        dict: Updated state with task result and findings
    """
    # Get current task from Send metadata
    current_task_data = state.get("current_task")
    if not current_task_data:
        return {"execution_path": ["research_worker"]}

    # Validate task data has required fields
    if not isinstance(current_task_data, dict):
        return {"execution_path": ["research_worker"]}

    required_fields = ["task_id", "task_type", "description", "query"]
    if not all(field in current_task_data for field in required_fields):
        return {"execution_path": ["research_worker"]}

    task = ResearchTask(**current_task_data)  # type: ignore[arg-type]

    # Execute task based on type
    result = ""
    sources = []

    if task.task_type == TaskType.SEARCH:
        result, sources = await _execute_search(task.query)
    elif task.task_type == TaskType.SUMMARIZE:
        result = await _execute_summarize(task.query)
    elif task.task_type == TaskType.COMPARE:
        result = await _execute_compare(task.query)
    elif task.task_type == TaskType.ANALYZE:
        result = await _execute_analyze(task.query)
    else:
        result = f"Executed: {task.description}"

    # Store task result
    task_results = state.get("task_results", {})
    task_results[task.task_id] = result

    # Accumulate findings
    findings = state.get("research_findings", [])
    findings.append(result)

    # Accumulate sources
    research_sources = state.get("research_sources", [])
    research_sources.extend(sources)

    # Mark task as visited
    visited_tasks = state.get("visited_tasks", [])
    visited_tasks.append(task.task_id)

    # Increment iteration
    current_iteration = state.get("current_iteration", 0) + 1

    return {
        "task_results": task_results,
        "research_findings": findings,
        "research_sources": research_sources,
        "visited_tasks": visited_tasks,
        "current_iteration": current_iteration,
        "accumulated_confidence": min(
            1.0, state.get("accumulated_confidence", 0.0) + 0.2
        ),
        "execution_path": ["research_worker"],
    }


async def _execute_search(query: str) -> tuple[str, list[str]]:
    """Execute search task.

    TODO: Integrate with SearXNG search backend.
    """
    # Mock search result
    result = f"Search results for: {query}"
    sources = ["search:mock_source"]
    return result, sources


async def _execute_summarize(query: str) -> str:
    """Execute summarization task.

    TODO: Integrate with DSPy summarization module.
    """
    return f"Summary of: {query}"


async def _execute_compare(query: str) -> str:
    """Execute comparison task.

    TODO: Integrate with DSPy comparison module.
    """
    return f"Comparison: {query}"


async def _execute_analyze(query: str) -> str:
    """Execute analysis task.

    TODO: Integrate with DSPy analysis module.
    """
    return f"Analysis of: {query}"

"""Event emission utilities for progress tracking."""

from typing import AsyncGenerator

from agentx.agent.nodes.tracking.tracker import ProgressTracker
from agentx.domain.models.graph_state import AgentState


def get_progress_message(state: AgentState) -> str:
    """Get progress message for display.

    Args:
        state: Current agent state

    Returns:
        str: Progress message
    """
    iteration = state.get("current_iteration", 0)
    findings = state.get("research_findings", [])

    if iteration == 0:
        return "Planning query..."
    elif len(findings) == 0:
        return f"Searching for information (iteration {iteration})..."
    else:
        return (
            f"Analyzing findings (iteration {iteration}, {len(findings)} findings)..."
        )


async def progress_tracker_node(state: AgentState) -> AsyncGenerator[dict, None]:
    """Track progress during task execution.

    Args:
        state: Current agent state

    Yields:
        dict: Streaming event updates
    """
    plan = state.get("execution_plan")
    total_steps = len(plan.research_tasks) if plan else 5

    tracker = ProgressTracker(
        task_name="research",
        total_steps=total_steps,
    )

    async for update in tracker.track(state):
        yield update

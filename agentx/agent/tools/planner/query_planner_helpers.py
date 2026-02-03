"""Helper functions for QueryPlannerModule.

Provides utilities for building guidance context and parsing tasks.
"""

import json

from agentx.domain.models.query_plan import ResearchTask, TaskType


def build_guidance_context(search_guidance: dict | None) -> str:
    """Build guidance context string from search guidance dict.

    Args:
        search_guidance: Optional memory-guided search parameters

    Returns:
        Formatted guidance context string
    """
    if not search_guidance:
        return ""

    depth = search_guidance.get("search_depth", "medium")
    terms = search_guidance.get("prioritized_terms", "")
    sources = search_guidance.get("source_preferences", "")
    format_pref = search_guidance.get("answer_format", "")

    guidance_parts = []
    if depth:
        guidance_parts.append(f"Search depth: {depth}")
    if terms:
        guidance_parts.append(f"Priority terms: {terms}")
    if sources:
        guidance_parts.append(f"Preferred sources: {sources}")
    if format_pref:
        guidance_parts.append(f"Answer format: {format_pref}")

    return " | ".join(guidance_parts) if guidance_parts else ""


def parse_task_descriptions(
    task_descriptions_json: str, query: str, needs_research: bool
) -> list[ResearchTask]:
    """Parse task descriptions from JSON string.

    Args:
        task_descriptions_json: JSON string of task descriptions
        query: Original query (for fallback)
        needs_research: Whether research is needed

    Returns:
        List of ResearchTask objects
    """
    tasks: list[ResearchTask] = []

    try:
        task_data_list = json.loads(task_descriptions_json)
        for task_data in task_data_list:
            task = ResearchTask(
                task_id=task_data.get("task_id", f"task_{len(tasks)}"),
                task_type=TaskType(task_data.get("task_type", "search")),
                description=task_data.get("description", ""),
                query=task_data.get("query", query),
                dependencies=task_data.get("dependencies", []),
            )
            tasks.append(task)
    except (json.JSONDecodeError, ValueError):
        # Default: single search task if parsing fails and research is needed
        if needs_research:
            tasks = [
                ResearchTask(
                    task_id="search_1",
                    task_type=TaskType.SEARCH,
                    description="Search for information",
                    query=query,
                    dependencies=[],
                )
            ]

    return tasks


def parse_duration(duration_str: str | None) -> int | None:
    """Parse estimated duration from string.

    Args:
        duration_str: Duration string or None

    Returns:
        Integer duration or None
    """
    if not duration_str:
        return None

    try:
        return int(duration_str)
    except ValueError:
        return None


__all__ = [
    "build_guidance_context",
    "parse_task_descriptions",
    "parse_duration",
]

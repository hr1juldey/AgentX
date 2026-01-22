# =============================================================================
# AGENTX Multi-Hop Search - Hop Helpers
# =============================================================================
# Shared helper functions for hop execution
# =============================================================================

from __future__ import annotations

from typing import Any

import dspy

from services.multihop_search.search_client import SearchResultItem


def send_progress_event(
    callback: Any,
    event_type: str,
    hop_number: int,
    total_hops: int,
    message: str,
    progress: float,
    eta_seconds: float | None = None,
    documents_found: int = 0,
    query_used: str | None = None,
    reflection_reasoning: str | None = None,
) -> None:
    """Send progress update via callback."""
    if callback is None:
        return

    from services.multihop_search.schemas import HopEvent

    event = HopEvent(
        event_type=event_type,
        hop_number=hop_number,
        total_hops=total_hops,
        message=message,
        progress=progress,
        eta_seconds=eta_seconds,
        documents_found=documents_found,
        query_used=query_used,
        reflection_reasoning=reflection_reasoning,
    )

    try:
        callback(event)
    except Exception:
        pass


def summarize_documents(documents: list[SearchResultItem]) -> str:
    """Create brief summary for assessment."""
    if not documents:
        return "No documents found."

    summaries: list[str] = []
    for i, doc in enumerate(documents[:5]):
        title = doc.title or "Untitled"
        content = doc.content[:150] + "..." if len(doc.content) > 150 else doc.content
        summaries.append(f"{i + 1}. {title}: {content}")

    return "\n".join(summaries)


def build_search_context(results: list[Any]) -> str:
    """Build context string from search results."""
    context_parts: list[str] = []
    for i, result in enumerate(results):  # type: ignore[bad-argument-type]
        context_parts.append(f"[{i + 1}] {result.title}\n{result.content}")
    return "\n\n".join(context_parts)


def generate_search_query(
    question: str,
    hop_num: int,
    plan_result: Any,
) -> tuple[str, str]:
    """Generate search query for this hop.

    Returns:
        Tuple of (search_query, strategy)
    """
    if hop_num == 1:
        return question, "INITIAL"
    elif plan_result is not None:
        return (
            plan_result.next_query,  # type: ignore[missing-attribute]
            plan_result.strategy,  # type: ignore[missing-attribute]
        )
    else:
        return f"{question} details", "REFINE_TOPIC"


def generate_hop_answer(
    answer_module: dspy.ChainOfThought,
    question: str,
    context: str,
) -> str:
    """Generate answer for current hop context.

    Args:
        answer_module: DSPy answer module
        question: User's question
        context: Search context

    Returns:
        Generated answer string
    """
    hop_result = answer_module(  # type: ignore[bad-return]
        question=question,
        context=context,
    )
    return hop_result.answer  # type: ignore[missing-attribute]

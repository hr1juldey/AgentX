"""Synthesizer node for the dynamic agent graph.

This node generates the final response using accumulated research findings
and streams tokens to the frontend for progressive disclosure.
"""

from typing import AsyncGenerator

from agentx.application.services.synthesis import SynthesisService
from agentx.domain.models.graph_state import AgentState
from agentx.domain.models.streaming_events import (
    CompleteEvent,
    StreamingEventType,
    TokenEvent,
    WidgetRevealEvent,
)


async def synthesizer_node(state: AgentState) -> AsyncGenerator[dict, None]:
    """Synthesize response with progressive disclosure.

    Streams text first, then reveals widgets progressively.
    Uses SynthesisService for multi-source synthesis with consensus
    and conflict detection.

    Args:
        state: Current agent state

    Yields:
        dict: Streaming events and final state updates
    """
    findings = state.get("research_findings", [])
    widgets = state.get("selected_widgets", [])
    query = state.get("query", "")

    # Phase 1: Stream text response with DSPy-powered synthesis
    response_parts: list[str] = []

    # Multi-source synthesis using SynthesisService
    synthesis_service = SynthesisService()

    # Prepare assessed sources from research findings
    assessed_sources = [
        {
            "content": finding,
            "relevance_score": 0.8,
            "quality_score": 0.8,
        }
        for finding in findings
    ]

    # Run multi-source synthesis
    synthesized = await synthesis_service.synthesize(
        query=query,
        assessed_sources=assessed_sources,
    )

    # Use synthesized unified answer with consensus/conflict info
    response_text = synthesized["unified_answer"]

    # Append consensus and conflict info if available
    if synthesized.get("consensus_points"):
        response_text += (
            f"\n\n**Key Consensus Points:**\n{synthesized['consensus_points']}"
        )
    if synthesized.get("conflicts"):
        response_text += f"\n\n**Noted Conflicts:**\n{synthesized['conflicts']}"

    # Store synthesis metadata in state
    synthesis_metadata = {
        "consensus_points": synthesized.get("consensus_points", ""),
        "conflicts": synthesized.get("conflicts", ""),
        "confidence_level": synthesized.get("confidence_level", "unknown"),
        "reasoning": synthesized.get("reasoning", ""),
    }

    for i, char in enumerate(response_text):
        response_parts.append(char)
        yield {
            "streaming_event": TokenEvent(
                event_type=StreamingEventType.TOKEN,
                token=char,
                is_first=(i == 0),
                index=i,
            ),
        }

    final_response = "".join(response_parts)

    # Phase 2: Reveal widgets progressively (highest priority first)
    widgets_sorted = sorted(widgets, key=lambda w: w.priority, reverse=True)

    for i, widget in enumerate(widgets_sorted):
        yield {
            "streaming_event": WidgetRevealEvent(
                event_type=StreamingEventType.WIDGET_REVEAL,
                widget=widget.model_dump(),
                index=i,
                total=len(widgets_sorted),
            ),
        }

    # Phase 3: Final completion event
    yield {
        "final_response": final_response,
        "widgets": widgets_sorted,
        "widget_count": len(widgets_sorted),
        "synthesis_metadata": synthesis_metadata,
        "streaming_event": CompleteEvent(
            event_type=StreamingEventType.COMPLETE,
            final_response=final_response,
            widget_count=len(widgets_sorted),
            total_duration=0.0,  # TODO: Track actual duration
        ),
        "execution_path": ["synthesizer"],
    }


def direct_answer_node(state: AgentState) -> dict:
    """Provide direct answer without research.

    Used for simple queries (0 tasks) that don't need research.

    Args:
        state: Current agent state

    Returns:
        dict: Final state with direct answer
    """
    query = state["query"]

    # Simple direct answer (no research needed)
    # TODO: Integrate with LLM backend for actual responses
    response = f"I'll answer: {query}"

    return {
        "final_response": response,
        "selected_widgets": [],
        "widget_count": 0,
        "execution_path": ["direct_answer"],
    }

"""Synthesizer node for the dynamic agent graph.

This node generates the final response using accumulated research findings
and streams tokens to the frontend for progressive disclosure.
"""

from typing import AsyncGenerator

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

    Args:
        state: Current agent state

    Yields:
        dict: Streaming events and final state updates
    """
    findings = state.get("research_findings", [])
    widgets = state.get("selected_widgets", [])

    # Phase 1: Stream text response
    response_parts: list[str] = []
    findings_text = "\n".join(f"- {f}" for f in findings)

    # Simple synthesis: combine findings into coherent response
    # TODO: Replace with DSPy SynthesizerModule when implemented
    # Stream tokens (mock streaming for now)
    # TODO: Integrate with DSPy streaming when LLM backend is configured
    response_text = f"Based on my research, here's what I found:\n\n{findings_text}"

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

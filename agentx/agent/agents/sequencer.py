"""Sequencer agent wrapper for Real AgentX v0.1.

Ported from R014: services/pipeline/sequencer.py

Wraps the sequencer node as a standalone agent.
Implements staggered delivery pattern for widget presentation.
"""

from __future__ import annotations

from typing import Any

from agentx.agent.nodes.sequencer import sequencer_node
from agentx.agent.state import AgentState
from agentx.core.dependencies import ensure_dspy_configured


# Global singleton instance
_sequencer_agent_wrapper: SequencerAgentWrapper | None = None


class SequencerAgentWrapper:
    """Wrapper for the sequencer node.

    Provides a clean interface for running the sequencer agent
    outside of the full LangGraph pipeline.
    """

    def __init__(self) -> None:
        """Initialize the sequencer agent wrapper."""
        self._initialized = False

    async def sequence_widgets(
        self,
        widgets: list[dict],
        urgency: str = "routine",
        session_id: str = "default",
    ) -> dict[str, Any]:
        """Sequence and pace widgets for delivery.

        Args:
            widgets: List of widget dicts to sequence
            urgency: Urgency level (immediate, routine, background)
            session_id: Optional session identifier

        Returns:
            dict with widget sequence and timing
        """
        # Ensure DSPy is configured
        ensure_dspy_configured()

        # Create minimal state
        state: AgentState = {
            "messages": [],
            "ui": [],
            "reasoning_steps": 5,
            "session_id": session_id,
            "total_tool_calls": 0,
            "_widget_selection": {
                "widget_type": widgets[-1].get("type", "card") if widgets else "card",
                "existing_widgets": [w.get("type", "") for w in widgets[:-1]],
            },
            "_analysis": {
                "urgency": urgency,
            },
        }

        # Run sequencer node
        result = await sequencer_node(state)

        return result


def get_sequencer_agent() -> SequencerAgentWrapper:
    """Get the sequencer agent wrapper singleton.

    Returns:
        SequencerAgentWrapper: The sequencer agent wrapper instance.
    """
    ensure_dspy_configured()
    global _sequencer_agent_wrapper
    if _sequencer_agent_wrapper is None:
        _sequencer_agent_wrapper = SequencerAgentWrapper()
    return _sequencer_agent_wrapper

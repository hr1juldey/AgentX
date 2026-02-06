"""State definitions for LangGraph conversation graphs.

This module defines the shared state schema used by the conversation graph
and its nodes. Following CLAUDE_POLICY.md: Absolute imports only.
"""

import dspy
from typing import NotRequired, Required, TypedDict


class ChatState(TypedDict):
    """State for conversation graph using TypedDict (codebase standard).

    User Decision: Store conversation_history in BOTH graph state (for
    checkpointing) AND agent internal (for DSPy context) - redundant but safe.
    """

    # Required fields (must be present)
    query: Required[str]
    user_id: Required[str]
    session_id: Required[str]
    input_mode: Required[str]

    # Optional fields (can be absent - populated by nodes during execution)
    conversation_history: NotRequired[dspy.History]
    agent_response: NotRequired[str]
    formatted_response: NotRequired[str]
    error: NotRequired[str]


__all__ = ["ChatState"]

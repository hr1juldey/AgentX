"""Thread storage and state management for Real AgentX v0.1.

Provides in-memory thread storage with state serialization utilities.
Can be replaced with Redis/database for persistence.
"""

from datetime import datetime, timezone
from uuid import uuid4

from agentx.agent.state import AgentState


# In-memory thread storage (can be replaced with Redis/database later)
_threads: dict[str, dict] = {}


def get_threads() -> dict[str, dict]:
    """Get the threads storage dictionary.

    Returns:
        Dictionary mapping thread_id to thread data
    """
    return _threads


def create_thread_state(thread_id: str | None = None) -> dict:
    """Create a new thread state.

    Args:
        thread_id: Optional thread ID (generated if not provided)

    Returns:
        Thread data dictionary
    """
    tid = thread_id or str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    return {
        "thread_id": tid,
        "created_at": now,
        "updated_at": now,
        "state": {
            "messages": [],
            "ui": [],
            "session_id": tid,
            "reasoning_steps": 0,
            "total_tool_calls": 0,
        },
    }


def serialize_state(state: AgentState) -> dict:
    """Serialize AgentState to JSON-compatible dict.

    Args:
        state: AgentState to serialize

    Returns:
        JSON-compatible dict representation
    """
    return {
        "messages": [
            {
                "role": msg.type if hasattr(msg, "type") else "ai",
                "content": msg.content
                if isinstance(msg.content, str)
                else str(msg.content),
            }
            for msg in state.get("messages", [])
        ],
        "ui": state.get("ui", []),
        "session_id": state.get("session_id"),
        "reasoning_steps": state.get("reasoning_steps", 0),
        "total_tool_calls": state.get("total_tool_calls", 0),
        "contextualized_data": state.get("contextualized_data"),
        "values": state,  # Full state for LangGraph SDK compatibility
    }


def generate_event(event_type: str, data: dict) -> str:
    """Generate SSE event string.

    Args:
        event_type: Event type (e.g., "messages/partial", "messages/complete")
        data: Event data

    Returns:
        SSE-formatted string
    """
    import json

    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"

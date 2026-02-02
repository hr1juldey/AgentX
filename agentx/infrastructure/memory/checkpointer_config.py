"""Graph memory configuration using LangGraph Checkpointers.

This module provides the checkpointer for graph memory (procedural routing).
Graph memory stores AgentState snapshots for time-travel debugging.

Redis checkpointer is managed by the application lifespan context.
"""

from langgraph.checkpoint.redis.aio import AsyncRedisSaver  # type: ignore[import]

# Global checkpointer instance (set by lifespan)
_checkpointer: AsyncRedisSaver | None = None


def get_checkpointer() -> AsyncRedisSaver:
    """Get checkpointer for graph memory.

    Graph Memory (Checkpointers):
    - Purpose: Procedural routing, "how to navigate"
    - Duration: Per-thread, time-travel enabled
    - Stores: AgentState snapshots, execution path, routing history

    Returns:
        AsyncRedisSaver: LangGraph checkpointer instance

    Raises:
        RuntimeError: If checkpointer is not initialized (lifespan not started)
    """
    global _checkpointer
    if _checkpointer is None:
        msg = "Checkpointer not initialized. Start the application to initialize Redis connections."
        raise RuntimeError(msg)
    return _checkpointer


def set_checkpointer(checkpointer: AsyncRedisSaver) -> None:
    """Set the global checkpointer instance.

    Called by lifespan context manager during startup.

    Args:
        checkpointer: LangGraph checkpointer instance
    """
    global _checkpointer
    _checkpointer = checkpointer

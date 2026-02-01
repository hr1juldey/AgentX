"""Graph memory configuration using LangGraph Checkpointers.

This module provides the checkpointer for graph memory (procedural routing).
Graph memory stores AgentState snapshots for time-travel debugging.
"""

from functools import lru_cache

from langgraph.checkpoint.postgres import PostgresSaver  # type: ignore[import]


@lru_cache
def get_checkpointer() -> PostgresSaver:
    """Get checkpointer for graph memory.

    Graph Memory (Checkpointers):
    - Purpose: Procedural routing, "how to navigate"
    - Duration: Per-thread, time-travel enabled
    - Stores: AgentState snapshots, execution path, routing history

    Returns:
        PostgresSaver: LangGraph checkpointer instance
    """
    DB_URI = "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"
    return PostgresSaver.from_conn_string(DB_URI)

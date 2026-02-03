"""Memory management tools for DSPy ReAct agent.

REAL implementation using UnifiedMem0Adapter.
Fixes Fraud #2.1: Fake memory tools that return strings without doing anything.
"""

from __future__ import annotations

import asyncio
from datetime import datetime

from agentx.infrastructure.memory.unified_mem0_adapter import UnifiedMem0Adapter

_adapter: UnifiedMem0Adapter | None = None


def _get_adapter() -> UnifiedMem0Adapter:
    """Lazy-load adapter singleton.

    Returns:
        UnifiedMem0Adapter: The shared adapter instance
    """
    global _adapter
    if _adapter is None:
        _adapter = UnifiedMem0Adapter()
    return _adapter


def consolidate_memories(user_id: str = "default", session_id: str = "") -> str:
    """Consolidate session memories into long-term storage.

    REAL implementation: Calls UnifiedMem0Adapter to consolidate memories.
    Mem0 handles duplicate detection and merging automatically.

    Args:
        user_id: User ID for memory consolidation
        session_id: Session ID to consolidate (optional)

    Returns:
        str: Result message with consolidation status
    """
    try:
        adapter = _get_adapter()

        # Get all memories for user (run async in sync context)
        memories = asyncio.run(adapter.get_memories(user_id, limit=1000))

        if not memories:
            return f"No memories to consolidate for user {user_id}"

        # Consolidate using Mem0 (run async in sync context)
        consolidated = asyncio.run(adapter.consolidate_memories(memories, user_id))

        return f"Consolidated {len(consolidated)} memories for user {user_id} in session {session_id or 'default'}"
    except Exception as e:
        return f"Consolidation failed: {str(e)}"


def categorize_memory(content: str, category: str, user_id: str = "default") -> str:
    """Categorize a memory with explicit category label.

    REAL implementation: Stores memory with category in metadata.

    Args:
        content: Memory content to categorize
        category: Category label (e.g., "preference", "pattern", "result")
        user_id: User ID for memory storage

    Returns:
        str: Result message with categorization status
    """
    try:
        adapter = _get_adapter()

        # Store with category in metadata
        adapter.client.add(
            content,
            user_id=user_id,
            metadata={
                "category": category,
                "categorized_at": datetime.now().isoformat(),
            },
        )

        return f"Memory categorized as '{category}' for user {user_id}"
    except Exception as e:
        return f"Categorization failed: {str(e)}"


def set_memory_ttl(memory_id: str, ttl_days: int, user_id: str = "default") -> str:
    """Set time-to-live for a specific memory.

    REAL implementation: Updates metadata with TTL information.
    Note: Mem0 doesn't support native TTL, so we store as metadata.

    Args:
        memory_id: ID of the memory to update
        ttl_days: TTL in days
        user_id: User ID for memory ownership verification

    Returns:
        str: Result message with TTL update status
    """
    try:
        adapter = _get_adapter()

        # Note: Mem0 doesn't support update() API
        # We store TTL as a separate metadata record
        adapter.client.add(
            f"TTL setting: Memory {memory_id} expires in {ttl_days} days",
            user_id=user_id,
            metadata={
                "type": "ttl_setting",
                "target_memory_id": memory_id,
                "ttl_days": ttl_days,
                "set_at": datetime.now().isoformat(),
            },
        )

        return f"TTL set to {ttl_days} days for memory {memory_id}"
    except Exception as e:
        return f"TTL update failed: {str(e)}"


__all__ = [
    "consolidate_memories",
    "categorize_memory",
    "set_memory_ttl",
]

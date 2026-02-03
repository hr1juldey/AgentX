"""Data models for RAG Conflict Resolution domain."""

from dataclasses import dataclass
from typing import Optional

from agentx.domain.entities.memory_record import MemoryRecord


@dataclass
class ConflictResolutionResult:
    """Result of conflict resolution process."""

    resolved_memory: Optional[MemoryRecord] = None
    conflicts_detected: int = 0
    conflicts_resolved: int = 0
    llm_fallback_used: bool = False
    resolution_tier: str = "none"
    reasoning: str = ""


__all__ = ["ConflictResolutionResult"]

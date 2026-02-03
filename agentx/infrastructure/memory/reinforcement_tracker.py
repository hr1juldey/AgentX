"""Reinforcement tracker for memory TTL adjustment.

Logs retrieval outcomes and adjusts TTL based on performance.
More retrieval = stronger connections = longer TTL.
Bad retrievals = shorter TTL.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from agentx.domain.entities.memory_record import MemoryRecord


@dataclass
class RetrievalEvent:
    """A single retrieval event."""

    memory_id: UUID
    success: bool
    quality_score: float
    timestamp: datetime = field(default_factory=datetime.now)


class ReinforcementTracker:
    """Tracks retrieval outcomes for TTL reinforcement.

    Implements: "More retrieval leads to stronger connections and longer TTL.
    Bad retrievals lead to shorter TTL."
    """

    def __init__(
        self,
        success_threshold: float = 0.7,
        failure_threshold: float = 0.3,
    ):
        """Initialize reinforcement tracker.

        Args:
            success_threshold: Quality above this extends TTL
            failure_threshold: Quality below this shortens TTL
        """
        self.success_threshold = success_threshold
        self.failure_threshold = failure_threshold

        self._events: dict[UUID, list[RetrievalEvent]] = defaultdict(list)
        self._success_count: dict[UUID, int] = defaultdict(int)
        self._failure_count: dict[UUID, int] = defaultdict(int)

    def log_outcome(
        self,
        memory_id: UUID,
        success: bool,
        quality_score: float,
    ) -> None:
        """Log retrieval outcome for a memory.

        Args:
            memory_id: Memory that was retrieved
            success: Whether retrieval was successful
            quality_score: Quality of the retrieval result
        """
        event = RetrievalEvent(
            memory_id=memory_id,
            success=success,
            quality_score=quality_score,
        )
        self._events[memory_id].append(event)

        if success and quality_score >= self.success_threshold:
            self._success_count[memory_id] += 1
        elif not success or quality_score <= self.failure_threshold:
            self._failure_count[memory_id] += 1

    def get_success_rate(self, memory_id: UUID) -> float:
        """Get success rate for a memory.

        Args:
            memory_id: Memory to check

        Returns:
            Success rate (0.0 to 1.0)
        """
        events = self._events.get(memory_id, [])
        if not events:
            return 0.5  # Neutral for new memories

        success_count = sum(1 for e in events if e.success)
        return success_count / len(events)

    def should_extend_ttl(self, memory_id: UUID) -> bool:
        """Check if TTL should be extended based on good performance.

        Args:
            memory_id: Memory to check

        Returns:
            True if TTL should be extended
        """
        success_rate = self.get_success_rate(memory_id)
        return success_rate >= 0.6 and self._success_count[memory_id] >= 3

    def should_shorten_ttl(self, memory_id: UUID) -> bool:
        """Check if TTL should be shortened based on bad performance.

        Args:
            memory_id: Memory to check

        Returns:
            True if TTL should be shortened
        """
        success_rate = self.get_success_rate(memory_id)
        return success_rate < 0.4 and self._failure_count[memory_id] >= 2

    async def apply_reinforcement(
        self,
        memory: MemoryRecord,
        context_rot_manager,
    ) -> MemoryRecord:
        """Apply reinforcement adjustments to memory TTL.

        Args:
            memory: Memory to adjust
            context_rot_manager: ContextRotManager for TTL adjustments

        Returns:
            Adjusted memory
        """
        if self.should_extend_ttl(memory.memory_id):
            context_rot_manager.extend_ttl(memory)
        elif self.should_shorten_ttl(memory.memory_id):
            context_rot_manager.shorten_ttl(memory)

        return memory

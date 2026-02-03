"""Context rotting prevention using TTL, supersede, decay, and reinforcement.

Prevents stale memories from polluting the retrieval context.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

from agentx.domain.entities.memory_record import MemoryRecord


@dataclass
class RotStatus:
    """Status of a memory after rot check."""

    is_expired: bool
    days_until_expiry: int | None
    decayed_quality: float
    should_supersede: bool


class ContextRotManager:
    """Manages context rotting prevention for memories.

    Uses multiple mechanisms:
    - TTL: Memories expire after a time period
    - Supersede: Better memories replace older ones
    - Decay: Quality scores degrade over time
    - Reinforcement: Good retrievals extend TTL, bad ones shorten it
    """

    def __init__(
        self,
        base_ttl_days: int = 30,
        decay_rate_per_day: float = 0.01,
        ttl_extension_days: int = 7,
        ttl_shorten_days: int = 7,
    ):
        """Initialize context rot manager.

        Args:
            base_ttl_days: Default time-to-live for memories
            decay_rate_per_day: How much quality decays per day
            ttl_extension_days: How much to extend TTL on good retrieval
            ttl_shorten_days: How much to shorten TTL on bad retrieval
        """
        self.base_ttl_days = base_ttl_days
        self.decay_rate_per_day = decay_rate_per_day
        self.ttl_extension_days = ttl_extension_days
        self.ttl_shorten_days = ttl_shorten_days

    def check_ttl(self, memory: MemoryRecord) -> RotStatus:
        """Check if memory has expired and provide status.

        Args:
            memory: Memory to check

        Returns:
            RotStatus with expiry information
        """
        # Check if superseded
        if memory.superseded_by is not None:
            return RotStatus(
                is_expired=True,
                days_until_expiry=0,
                decayed_quality=self.apply_decay(memory),
                should_supersede=True,
            )

        # Calculate days until expiry
        expiry_date = memory.created_at + timedelta(days=memory.ttl_days)
        days_left = (expiry_date - datetime.now()).days

        return RotStatus(
            is_expired=days_left <= 0,
            days_until_expiry=max(0, days_left),
            decayed_quality=self.apply_decay(memory),
            should_supersede=False,
        )

    def apply_decay(self, memory: MemoryRecord) -> float:
        """Apply quality decay based on age.

        Args:
            memory: Memory to decay

        Returns:
            Decayed quality score
        """
        age_days = (datetime.now() - memory.created_at).days
        decay_factor = max(0.0, 1.0 - (age_days * self.decay_rate_per_day))
        return memory.quality_score * decay_factor

    def extend_ttl(self, memory: MemoryRecord) -> None:
        """Extend TTL (used by reinforcement tracker for good retrievals)."""
        memory.extend_ttl(self.ttl_extension_days)

    def shorten_ttl(self, memory: MemoryRecord) -> None:
        """Shorten TTL (used by reinforcement tracker for bad retrievals)."""
        memory.shorten_ttl(self.ttl_shorten_days)

    def mark_superseded(
        self, old_memory: MemoryRecord, new_memory: MemoryRecord
    ) -> bool:
        """Mark old memory as superseded if new one is better.

        Args:
            old_memory: Existing memory
            new_memory: New potential replacement

        Returns:
            True if old memory was superseded
        """
        # Compare quality and recency
        if (
            new_memory.quality_score > old_memory.quality_score
            and new_memory.created_at > old_memory.created_at
        ):
            old_memory.superseded_by = new_memory.memory_id
            return True
        return False

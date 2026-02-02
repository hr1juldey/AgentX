"""Duration memory data models.

Defines state enum and event dataclass for duration tracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


class DurationState(str, Enum):
    """States for duration tracking."""

    STARTED = "started"
    ENDED = "ended"
    IN_PROGRESS = "in_progress"


@dataclass
class DurationEvent:
    """Duration memory event.

    Tracks state transitions (e.g., task started → task completed).
    """

    memory_id: UUID
    entity: str  # What the duration is about (e.g., "task", "meeting")
    state: DurationState
    timestamp: datetime
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            dict: Event data.
        """
        return {
            "memory_id": str(self.memory_id),
            "entity": self.entity,
            "state": self.state.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

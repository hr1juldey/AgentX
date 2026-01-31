"""Duration memory service for state tracking.

Tracks state transitions and consolidates duration events.
From C005 memory-rag change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from agentx.domain.entities.enums import TemporalType


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


class DurationMemoryService:
    """Service for tracking and consolidating duration memories.

    Features:
    - State transition tracking
    - Duration calculation
    - Consolidation of start → end events
    """

    def __init__(self) -> None:
        """Initialize duration memory service."""
        self._active_states: dict[str, DurationEvent] = {}

    def start_state(
        self, entity: str, metadata: dict[str, Any] | None = None
    ) -> DurationEvent:
        """Start tracking a state.

        Args:
            entity: Entity name (e.g., "task_abc").
            metadata: Optional metadata.

        Returns:
            DurationEvent: Started event.
        """
        event = DurationEvent(
            memory_id=uuid4(),
            entity=entity,
            state=DurationState.STARTED,
            timestamp=datetime.now(),
            metadata=metadata or {},
        )

        self._active_states[entity] = event
        return event

    def end_state(
        self, entity: str, metadata: dict[str, Any] | None = None
    ) -> DurationEvent | None:
        """End tracking a state.

        Args:
            entity: Entity name.
            metadata: Optional metadata.

        Returns:
            DurationEvent | None: Ended event, or None if not found.
        """
        start_event = self._active_states.get(entity)
        if not start_event:
            return None

        event = DurationEvent(
            memory_id=uuid4(),
            entity=entity,
            state=DurationState.ENDED,
            timestamp=datetime.now(),
            metadata={
                "start_event_id": str(start_event.memory_id),
                "start_timestamp": start_event.timestamp.isoformat(),
                **(metadata or {}),
            },
        )

        # Calculate duration
        duration = (event.timestamp - start_event.timestamp).total_seconds()
        event.metadata["duration_seconds"] = duration

        # Remove from active states
        del self._active_states[entity]

        return event

    def get_active_states(self) -> list[DurationEvent]:
        """Get all active (in-progress) states.

        Returns:
            list[DurationEvent]: Active state events.
        """
        return list(self._active_states.values())

    def consolidate_durations(
        self, entity: str, start_event: DurationEvent, end_event: DurationEvent
    ) -> dict[str, Any]:
        """Consolidate a start → end pair into a duration memory.

        Args:
            entity: Entity name.
            start_event: Start event.
            end_event: End event.

        Returns:
            dict: Consolidated duration memory.
        """
        duration = (end_event.timestamp - start_event.timestamp).total_seconds()

        return {
            "content": f"{entity} duration: {duration:.0f} seconds",
            "entity": entity,
            "start_time": start_event.timestamp.isoformat(),
            "end_time": end_event.timestamp.isoformat(),
            "duration_seconds": duration,
            "temporal_type": TemporalType.STATE,
            "metadata": {
                **start_event.metadata,
                **end_event.metadata,
            },
        }

    def get_duration_summary(self) -> dict[str, Any]:
        """Get summary of all tracked durations.

        Returns:
            dict: Duration summary.
        """
        active_count = len(self._active_states)

        return {
            "active_states": active_count,
            "tracked_entities": list(self._active_states.keys()),
            "timestamp": datetime.now().isoformat(),
        }

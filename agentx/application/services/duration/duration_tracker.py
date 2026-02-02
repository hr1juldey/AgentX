"""Duration tracking service.

Tracks state transitions and active states.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from agentx.application.services.duration.models import DurationEvent, DurationState


class DurationTracker:
    """Service for tracking duration state transitions.

    Features:
    - State transition tracking
    - Active state management
    - Duration calculation
    """

    def __init__(self) -> None:
        """Initialize duration tracker."""
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

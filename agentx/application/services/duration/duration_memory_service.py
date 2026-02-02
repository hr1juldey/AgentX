"""Duration memory service for state tracking.

Composes duration tracker and memory operations.
"""

from __future__ import annotations

from typing import Any

from agentx.application.services.duration.duration_tracker import DurationTracker
from agentx.application.services.duration.memory_operations import (
    DurationMemoryOperations,
)
from agentx.application.services.duration.models import DurationEvent


class DurationMemoryService:
    """Service for tracking and consolidating duration memories.

    Features:
    - State transition tracking
    - Duration calculation
    - Consolidation of start → end events
    """

    def __init__(self) -> None:
        """Initialize duration memory service."""
        self._tracker = DurationTracker()
        self._memory_ops = DurationMemoryOperations()

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
        return self._tracker.start_state(entity, metadata)

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
        return self._tracker.end_state(entity, metadata)

    def get_active_states(self) -> list[DurationEvent]:
        """Get all active (in-progress) states.

        Returns:
            list[DurationEvent]: Active state events.
        """
        return self._tracker.get_active_states()

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
        return self._memory_ops.consolidate_durations(entity, start_event, end_event)

    def get_duration_summary(self) -> dict[str, Any]:
        """Get summary of all tracked durations.

        Returns:
            dict: Duration summary.
        """
        return self._tracker.get_duration_summary()

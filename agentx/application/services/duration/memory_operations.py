"""Duration memory operations.

Handles consolidation of duration events into memories.
"""

from __future__ import annotations

from typing import Any

from agentx.application.services.duration.models import DurationEvent
from agentx.domain.entities.enums import TemporalType


class DurationMemoryOperations:
    """Operations for consolidating duration events."""

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

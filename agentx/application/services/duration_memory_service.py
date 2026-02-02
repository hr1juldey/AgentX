"""Duration memory service for state tracking.

Tracks state transitions and consolidates duration events.
From C005 memory-rag change.

This is a facade for backward compatibility. Actual implementation has been
moved to the duration/ subdirectory.
"""

from agentx.application.services.duration import DurationMemoryService

__all__ = ["DurationMemoryService"]

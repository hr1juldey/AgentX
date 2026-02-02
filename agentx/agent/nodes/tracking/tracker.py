"""Progress tracker class for transient UX.

Tracks progress and emits events every 1-2 seconds during long-running AI tasks.
"""

import time
from enum import Enum
from typing import AsyncGenerator

from agentx.domain.models.graph_state import AgentState
from agentx.domain.models.streaming_events import (
    BackgroundPromptEvent,
    CompleteEvent,
    ProgressEvent,
    StreamingEventType,
)


class ProgressStatus(str, Enum):
    """Status of task execution."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


async def _async_sleep(seconds: float) -> None:
    """Async sleep for progress tracking.

    Using asyncio.sleep for async compatibility.
    """
    import asyncio

    await asyncio.sleep(seconds)


class ProgressTracker:
    """Track progress and emit events for long-running tasks.

    Emits ProgressEvent every 1-2 seconds and BackgroundPromptEvent after 15s.
    """

    def __init__(self, task_name: str, total_steps: int = 5):
        """Initialize progress tracker.

        Args:
            task_name: Name of the task being tracked
            total_steps: Total number of steps (for progress calculation)
        """
        self.task_name = task_name
        self.total_steps = total_steps
        self.current_step = 0
        self.status = ProgressStatus.PENDING
        self.start_time = time.time()
        self.last_emit_time = 0.0
        self.emitted_background_prompt = False

    async def track(self, state: AgentState) -> AsyncGenerator[dict, None]:
        """Track progress and emit events.

        Yields streaming events at regular intervals.

        Args:
            state: Current agent state

        Yields:
            dict: Streaming event updates
        """
        self.status = ProgressStatus.IN_PROGRESS
        self.start_time = time.time()

        while self.status == ProgressStatus.IN_PROGRESS:
            current_time = time.time()
            elapsed = current_time - self.start_time

            # Emit progress every 1-2 seconds
            if current_time - self.last_emit_time >= 1.0:
                self.current_step = state.get("current_iteration", 0)
                progress = min(1.0, self.current_step / self.total_steps)

                yield {
                    "streaming_event": ProgressEvent(
                        event_type=StreamingEventType.PROGRESS,
                        progress=progress,
                        message=f"Processing {self.task_name}... (Step {self.current_step}/{self.total_steps})",
                        current_step=f"step_{self.current_step}",
                        total_steps=self.total_steps,
                    ),
                }

                self.last_emit_time = current_time

            # Emit background prompt after 15 seconds
            if elapsed >= 15.0 and not self.emitted_background_prompt:
                yield {
                    "streaming_event": BackgroundPromptEvent(
                        event_type=StreamingEventType.BACKGROUND_PROMPT,
                        elapsed_seconds=int(elapsed),
                        message="Task is taking longer. Continue in background?",
                    ),
                }
                self.emitted_background_prompt = True

            # Check for completion
            if state.get("final_response"):
                self.status = ProgressStatus.COMPLETED
                break

            await self._sleep_until_next_emit()

        # Emit completion event
        total_duration = time.time() - self.start_time
        final_resp = state.get("final_response", "")
        final_resp = final_resp if isinstance(final_resp, str) else ""
        yield {
            "streaming_event": CompleteEvent(
                event_type=StreamingEventType.COMPLETE,
                final_response=final_resp,
                widget_count=len(state.get("selected_widgets", [])),
                total_duration=total_duration,
            ),
        }

    async def _sleep_until_next_emit(self) -> None:
        """Sleep until next emit time."""
        await _async_sleep(0.5)  # Check every 500ms

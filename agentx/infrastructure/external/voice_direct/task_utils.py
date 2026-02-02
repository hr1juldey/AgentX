"""Task coordination utilities for voice direct handling.

Provides helper functions for managing async task coordination.
"""

import asyncio
import logging


logger = logging.getLogger(__name__)


async def wait_for_first_completed(
    *tasks: asyncio.Task,
) -> tuple[set[asyncio.Task], set[asyncio.Task]]:
    """Wait for first task to complete and cancel others.

    Args:
        *tasks: Tasks to wait for

    Returns:
        Tuple of (completed tasks, pending tasks)
    """
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    # Cancel pending tasks immediately
    for task in pending:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass  # Expected

    return done, pending


def cancel_pending_tasks(*tasks: asyncio.Task | None) -> None:
    """Cancel any pending tasks.

    Args:
        *tasks: Tasks to cancel
    """
    for task in tasks:
        if task and not task.done():
            task.cancel()

# =============================================================================
# AGENTX Researcher - Search Async Wrapper
# =============================================================================
# Handles async execution in sync context for SearXNG search
# =============================================================================

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Coroutine


def run_async_in_sync_context(coro: Coroutine[Any, Any, Any]) -> Any:
    """Run async coroutine in sync context, handling event loop conflicts.

    Detects if an event loop is already running and creates a new thread
    with its own loop if needed. This allows async code to work from
    sync contexts without conflicts.

    Args:
        coro: Async coroutine to execute

    Returns:
        Result of the coroutine execution
    """
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # Create new thread with its own event loop
        with ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    else:
        return asyncio.run(coro)

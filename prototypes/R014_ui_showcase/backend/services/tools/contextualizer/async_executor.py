# =============================================================================
# AGENTX Contextualizer - Async Executor Utility
# =============================================================================
# Reusable parallel execution for DSPy modules with semaphore protection
# =============================================================================

import asyncio
from typing import Any, Callable


async def execute_parallel(
    items: list[Any],
    processor: Callable,
    semaphore: asyncio.Semaphore,
) -> list:
    """Execute processing tasks in parallel with semaphore protection.

    Args:
        items: List of items to process
        processor: Async function that takes (item, semaphore) and returns result
        semaphore: Semaphore to limit concurrent LLM calls

    Returns:
        List of non-None results from processing
    """
    tasks = [processor(item, semaphore) for item in items]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]

# =============================================================================
# AGENTX Safe Async Executor
# =============================================================================
# Executor that safely handles async operations with fallback
# =============================================================================

import asyncio
import logging
from typing import Callable, TypeVar

from core.async_compat.hardware_detection import (
    HardwareTier,
    detect_hardware_tier,
    should_use_async,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


class SafeAsyncExecutor:
    """Executor that safely handles async operations with fallback.

    Automatically detects hardware and chooses optimal execution strategy.
    Falls back to sync execution when async is not beneficial.
    """

    def __init__(self, module_name: str):
        """Initialize executor with hardware-aware configuration.

        Args:
            module_name: Name of module for hardware detection
        """
        self.module_name = module_name
        self.use_async = should_use_async(module_name)
        self.tier = detect_hardware_tier()

        if self.use_async:
            logger.info(f"[{module_name}] ASYNC mode (tier: {self.tier})")
        else:
            logger.info(f"[{module_name}] SYNC mode (tier: {self.tier})")

    async def execute_async(self, coro):
        """Execute async operation.

        Args:
            coro: Coroutine to execute

        Returns:
            Result of coroutine
        """
        return await coro

    def execute_sync(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute sync operation.

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result of function
        """
        return func(*args, **kwargs)

    async def run_parallel(self, coroutines: list) -> list:
        """Run multiple coroutines in parallel or sequentially based on tier.

        Args:
            coroutines: List of coroutines to run

        Returns:
            List of results
        """
        if not self.use_async or self.tier == HardwareTier.BASIC:
            results = []
            for coro in coroutines:
                result = await coro
                results.append(result)
            return results

        return await asyncio.gather(*coroutines, return_exceptions=True)

# =============================================================================
# AGENTX Async Decorators
# =============================================================================
# Decorators for hybrid async/sync execution with graceful degradation
# =============================================================================

import asyncio
import functools
import logging

from core.async_compat.hardware_detection import should_use_async

logger = logging.getLogger(__name__)


def auto_async(module_name: str | None = None):
    """Decorator that makes functions work in both sync and async contexts.

    The decorated function can be called from sync or async contexts
    and will automatically adapt based on hardware capabilities.

    Args:
        module_name: Name of module for hardware detection

    Example:
        @auto_async("MyAgent")
        class MyAgent(dspy.Module):
            async def aforward(self, question: str) -> dspy.Prediction:
                return await self.llm(question=question)

        # Works both ways:
        result = agent(question="test")  # Sync call
        result = await agent.acall(question="test")  # Async call
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            name = module_name or func.__qualname__
            use_async = should_use_async(name)

            if not use_async:
                # Force sync path
                if asyncio.iscoroutinefunction(func):
                    return asyncio.run(func(*args, **kwargs))
                return func(*args, **kwargs)

            # Try async path
            if asyncio.iscoroutinefunction(func):
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Already in async context - return coroutine
                        return func(*args, **kwargs)
                    else:
                        # No loop - run async in sync context
                        return asyncio.run(func(*args, **kwargs))
                except RuntimeError:
                    return asyncio.run(func(*args, **kwargs))
            else:
                # Sync function - call directly
                return func(*args, **kwargs)

        return wrapper

    return decorator

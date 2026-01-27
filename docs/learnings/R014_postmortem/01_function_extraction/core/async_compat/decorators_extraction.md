# Function Postmortem: core/async_compat/decorators.py

## Metadata
- **File**: prototypes/R014_ui_showcase/backend/core/async_compat/decorators.py
- **Lines of Code**: 67
- **Purpose**: Decorators for hybrid async/sync execution with graceful degradation
- **Dependencies**: asyncio, functools, core.async_compat.hardware_detection

---

## Analysis

**Status**: Working decorator for adaptive async/sync execution

**Purpose**: Provides `@auto_async` decorator that makes functions work in both sync and async contexts, automatically adapting based on hardware capabilities.

**Architecture**: Decorator pattern with hardware-aware execution

---

## Functions/Classes Extracted

### auto_async (decorator factory)

**Purpose**: Decorator for hybrid async/sync function execution

**Signature**: `def auto_async(module_name: str | None = None)`

**Lines**: 16-66

**Key Code**:
```python
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
```

**What Works**:
- Detects hardware capabilities
- Handles both sync and async functions
- Checks for running event loop
- Falls back gracefully
- Good docstring with example

**Mistakes Found**:
- asyncio.run() can't be called nested (may cause issues)
- RuntimeError catch is too broad

**Behavioral Notes**:
- If hardware doesn't support async, forces sync
- If in async context, returns coroutine
- If not in async context, runs async with asyncio.run()
- Sync functions called directly

**Dependencies**:
- asyncio
- functools
- should_use_async from hardware_detection

**Reusability**: HIGH - Excellent adaptive pattern

---

## File Summary

**Assessment**: Innovative decorator for hardware-aware async/sync execution. Good concept but has some edge cases with nested asyncio.run().

**Key Learnings**:
1. Hardware detection can guide async/sync choice
2. Event loop state checking is important
3. Graceful degradation improves compatibility
4. functools.wraps preserves metadata

**Mistakes to Avoid**:
1. Don't nest asyncio.run() calls
2. Don't catch RuntimeError too broadly
3. Be careful with event loop management

**Recommendations**:
1. Detect existing event loop better
2. Consider using asyncio.create_task() when loop running
3. Add logging for mode selection

**Reusability Score**: HIGH - Good adaptive pattern with some edge cases

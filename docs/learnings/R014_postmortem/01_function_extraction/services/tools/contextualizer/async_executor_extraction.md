# Function Extraction: services/tools/contextualizer/async_executor.py

## File Overview
**Path**: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/tools/contextualizer/async_executor.py`
**Purpose**: Reusable parallel execution for DSPy modules with semaphore protection
**Lines**: 29

---

## Functions

### `execute_parallel()`

**Purpose**: Execute processing tasks in parallel with semaphore protection, filtering None results.

**Signature**:
```python
async def execute_parallel(
    items: list[Any],
    processor: Callable,
    semaphore: asyncio.Semaphore,
) -> list:
```

**Lines**: 11-28

**Key Code Snippet**:
```python
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
```

**What Works**:
1. **Automatic None filtering**: Filters out None results (useful for filter operations)
2. **Semaphore integration**: Passes semaphore to processor for throttling
3. **Simple interface**: Just items, processor, semaphore
4. **gather for parallelism**: asyncio.gather() runs all tasks concurrently

**Mistakes Found**:
None - clean utility function

**Behavioral Notes**:
- Creates tasks for all items upfront
- Runs all tasks in parallel (limited by semaphore)
- Filters None results automatically
- Returns only successful results

**Dependencies**:
- `asyncio.gather()` - Run coroutines concurrently
- `asyncio.Semaphore` - Limit concurrent operations

**Reusability**: Very High - Generic parallel execution pattern

---

## Key Patterns

1. **Parallel Task Creation Pattern**:
```python
tasks = [processor(item, semaphore) for item in items]
results = await asyncio.gather(*tasks)
```

2. **None Filtering Pattern**:
```python
return [r for r in results if r is not None]
```

3. **Semaphore Injection Pattern**:
```python
async def process_item(item, sem):
    async with sem:
        # LLM call

# In execute_parallel:
tasks = [processor(item, semaphore) for item in items]
```

---

## Lessons Learned

1. **Filter None automatically**: Makes filtering operations cleaner (return None to filter)
2. **Inject semaphore**: Passes semaphore to processor for flexible throttling
3. **Use gather for true parallelism**: gather() runs tasks concurrently
4. **Keep utilities simple**: Minimal parameters, clear purpose

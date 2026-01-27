# Function Extraction: services/tools/contextualizer/filter.py

## File Overview
**Path**: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/tools/contextualizer/filter.py`
**Purpose**: Filters noise and low-quality results
**Lines**: 101

---

## Classes and Functions

### `FilterModule` (DSPy Module)

**Purpose**: Filters noise and low-quality results with both sync and async execution.

**Signature**:
```python
class FilterModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.should_include = dspy.Predict(ShouldIncludeSignature)
        self.check_relevance = dspy.Predict(CheckRelevanceSignature)

    def forward(self, query: str, results: list) -> dict:
    async def aforward(self, query: str, results: list) -> dict:
```

**Lines**: 23-100

**Key Code Snippet (Sync)**:
```python
def forward(self, query: str, results: list) -> dict:
    """Filter results to remove noise."""
    filtered_results = []

    for result in results:
        include_result = self.should_include(query=query, result=str(result))
        relevance_result = self.check_relevance(query=query, result=str(result))

        # Safely convert bool
        should_include = _to_bool(
            include_result.should_include,
            default=True,
        )

        if should_include:
            result_copy = result.copy() if isinstance(result, dict) else result
            if isinstance(result_copy, dict):
                if hasattr(relevance_result, "relevance_score"):
                    result_copy["relevance_score"] = _to_float(
                        relevance_result.relevance_score
                    )
            filtered_results.append(result_copy)

    return {
        "filtered_data": filtered_results,
        "removed_count": len(results) - len(filtered_results),
    }
```

**Key Code Snippet (Async)**:
```python
async def aforward(self, query: str, results: list) -> dict:
    """Async filter results to remove noise with parallel processing."""

    async def filter_result(result, sem):
        async with sem:
            include_result = await self.should_include.acall(
                query=query, result=str(result)
            )
            relevance_result = await self.check_relevance.acall(
                query=query, result=str(result)
            )

            should_include = _to_bool(
                include_result.should_include,
                default=True,
            )

            if should_include:
                result_copy = result.copy() if isinstance(result, dict) else result
                if isinstance(result_copy, dict):
                    if hasattr(relevance_result, "relevance_score"):
                        result_copy["relevance_score"] = _to_float(
                            relevance_result.relevance_score
                        )
                return result_copy
            return None

    filtered_results = await execute_parallel(
        results, filter_result, _concurrency_semaphore
    )

    return {
        "filtered_data": filtered_results,
        "removed_count": len(results) - len(filtered_results),
    }
```

**What Works**:
1. **Two-stage filtering**: Should include + relevance score
2. **Safe type conversion**: _to_bool() with default=True (inclusive filtering)
3. **Relevance enrichment**: Adds relevance_score to kept results
4. **Count tracking**: Returns removed_count for monitoring

**Mistakes Found**:
None - robust filtering implementation

**Behavioral Notes**:
- Filters out low-quality/noise results
- Adds relevance_score to remaining results
- Returns count of removed items
- Parallel async processing for speed

**Dependencies**:
- `services.tools.contextualizer.signatures` - ShouldIncludeSignature, CheckRelevanceSignature
- `services.tools.common.type_utils` - _to_bool, _to_float
- `services.tools.contextualizer.async_executor` - execute_parallel

**Reusability**: High - Generic filtering for any query/results pair

---

## Key Patterns

1. **Two-Stage Filtering Pattern**:
```python
include_result = self.should_include(query=query, result=str(result))
relevance_result = self.check_relevance(query=query, result=str(result))

should_include = _to_bool(include_result.should_include, default=True)
```

2. **Inclusive Default Pattern**:
```python
should_include = _to_bool(include_result.should_include, default=True)
```
When in doubt, keep the result (inclusive filtering)

3. **Async Return None Pattern**:
```python
if should_include:
    return result_copy
return None  # Filtered out

# execute_parallel filters None: [r for r in results if r is not None]
```

---

## Lessons Learned

1. **Use inclusive defaults**: default=True means "when in doubt, keep it"
2. **Add metadata to kept results**: relevance_score helps with downstream ranking
3. **Track removals**: removed_count helps monitor filter aggressiveness
4. **Return None for filtered items**: execute_parallel automatically filters None

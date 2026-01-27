# Function Postmortem: services/tools/contextualizer/contextualizer.py

## Metadata
- **File**: services/tools/contextualizer/contextualizer.py
- **Lines of Code**: 84
- **Purpose**: Adds query context to search results with async parallel processing
- **Dependencies**: asyncio, dspy, settings, async_executor

---

## Analysis

**File Status**: PRODUCTION DSPy MODULE - ASYNC PARALLEL PATTERN

**Purpose**: Enriches search results with query-specific context using both sync and async parallel processing.

---

## Classes Extracted

### ContextualizerModule

**Purpose**: DSPy Module that adds query context to filtered results with concurrency control.

**Lines**: 18-84

**Key Code**:
```python
# Semaphore to limit concurrent LLM calls (prevents overwhelming Ollama)
_concurrency_semaphore = asyncio.Semaphore(settings.max_concurrent)

class ContextualizerModule(dspy.Module):
    """Adds query context to search results.

    Has 2 signatures:
    - AddQueryContext: Enrich results with query context
    - EnrichWithMetadata: Add relevant metadata
    """

    def __init__(self):
        super().__init__()
        self.add_context = dspy.Predict("query, result -> contextualized_result")
        self.enrich_metadata = dspy.Predict("result, metadata -> enriched_result")

    def forward(
        self, query: str, filtered_data: list, original_query: str = ""
    ) -> dict:
        """Contextualize filtered data."""
        contextualized_data = []
        query_str = original_query or query

        for result in filtered_data:
            context_result = self.add_context(query=query_str, result=str(result))

            result_copy = (
                result.copy() if isinstance(result, dict) else {"data": result}
            )
            if hasattr(context_result, "contextualized_result"):
                result_copy["query_context"] = context_result.contextualized_result  # type: ignore[attr-defined]

            contextualized_data.append(result_copy)

        return {
            "contextualized_data": contextualized_data,
            "query": query_str,
            "query_relevance": "High" if contextualized_data else "Low",
        }

    async def aforward(
        self, query: str, filtered_data: list, original_query: str = ""
    ) -> dict:
        """Async contextualize filtered data with parallel processing."""
        query_str = original_query or query

        async def contextualize_result(result, sem):
            async with sem:
                context_result = await self.add_context.acall(
                    query=query_str, result=str(result)
                )

                result_copy = (
                    result.copy() if isinstance(result, dict) else {"data": result}
                )
                if hasattr(context_result, "contextualized_result"):
                    result_copy["query_context"] = context_result.contextualized_result  # type: ignore[attr-defined]

                return result_copy

        contextualized_data = await execute_parallel(
            filtered_data, contextualize_result, _concurrency_semaphore
        )

        return {
            "contextualized_data": contextualized_data,
            "query": query_str,
            "query_relevance": "High" if contextualized_data else "Low",
        }
```

**What Works**:
- ✅ Module-level semaphore for concurrency control
- ✅ Both sync (forward) and async (aforward) implementations
- ✅ Parallel processing with execute_parallel helper
- ✅ Safe dict copying (preserves original)
- ✅ Type ignore comments for dynamic attributes
- ✅ Fallback for non-dict results (wraps in {"data": result})

**Mistakes Found**:
- ⚠️ enrich_metadata signature is defined but never used
- ⚠️ No error handling in async version
- ⚠️ Query relevance logic is simplistic (just checks if list is non-empty)

**Behavioral Notes**:
- Sync version processes sequentially (for loop)
- Async version processes in parallel with semaphore limiting
- Uses original_query if provided, otherwise uses query
- Adds "query_context" field to each result
- Returns query_relevance based on whether contextualized_data is non-empty

**Dependencies**:
- **Imports**: asyncio, dspy, settings, execute_parallel
- **Uses**: dspy.Predict(), async/await, asyncio.Semaphore, dict.copy()

**Reusability**: VERY HIGH - Async parallel pattern with semaphore control is production-ready

---

## File Summary

**Total Classes**: 1
**Lines of Code**: 84

**Overall Assessment**: EXCELLENT async parallel implementation. The module-level semaphore pattern is critical for preventing Ollama overload. Providing both sync and async versions is flexible.

**Key Learnings for Real AgentX**:
1. ✅ Use module-level semaphore for concurrency control: `_concurrency_semaphore = asyncio.Semaphore(settings.max_concurrent)`
2. ✅ Provide both sync (forward) and async (aforward) implementations
3. ✅ Use execute_parallel helper for batch processing with semaphore
4. ✅ Safe dict copying: `result.copy() if isinstance(result, dict) else {"data": result}`
5. ✅ Wrap non-dict results in dict for consistency
6. ✅ Use original_query fallback pattern
7. ⚠️ Add error handling in async version (try/except around acall)
8. ⚠️ Implement actual query relevance logic (not just list non-empty check)

**Reuse for Real AgentX**: ✅ DIRECT - This is the GOLD STANDARD for async batch processing with concurrency control

# data_contextualizer_async.py - Function Extraction

## File: services/pipeline/data_contextualizer_async.py

### Primary Purpose
Async implementation of DATA CONTEXTUALIZER with parallel processing for ~4x speedup.

### Key Functions

#### `async_contextualize_forward(agent, research_data: dict, original_query: str = "") -> dict`
**Purpose**: Async execute contextualizer pipeline with parallel LLM calls.

**Pipeline steps** (all async with `.aforward()`):
1. **Rerank**: `await agent.reranker.aforward(query, results)`
2. **Filter**: `await agent.filter.aforward(query, results)`
3. **Contextualize**: `await agent.contextualizer.aforward(query, filtered_data, original_query)`

**Performance**: ~4x speedup with 4 concurrent LLM calls per step.

**Returns**: Built contextualized return dict.

---

### Architectural Patterns

1. **Async parallelism**: All three steps use async forward passes
2. **Sequential steps**: Steps are still sequential (not parallel to each other)
3. **Type safety**: Uses `hasattr()` checks before `.get()` for coroutine handling
4. **Delegation**: Uses helper functions for metrics and building

---

### Dependencies

**Internal**:
- `services.pipeline.contextualizer_logging`: log_* functions
- `services.pipeline.data_contextualizer_builder`: build_contextualized_return
- `services.pipeline.data_contextualizer_utils`: extract_top_facts

---

### Lessons Learned

1. **Async provides 4x speedup**: Parallel LLM calls significantly faster than sequential
2. **Steps remain sequential**: Each step depends on previous step output
3. **Type ignore comments**: DSPy coroutines require type: ignore[bad-assignment]
4. **Safe dict access**: Use hasattr() checks before .get() on coroutines

# data_contextualizer_steps.py - Function Extraction

## File: services/pipeline/data_contextualizer_steps.py

### Primary Purpose
Individual step processing logic for contextualizer pipeline - extracts rerank, filter, contextualize steps.

### Key Functions

#### `execute_rerank_step(reranker, query: str, raw_data: list) -> tuple[dict, float]`
**Purpose**: Execute the reranking step with tracking and logging.

**Returns**: Tuple of (ranked_result, step_time)

**Side effects**:
- Tracks step in tracking system
- Logs step results

---

#### `execute_filter_step(filter_module, query: str, ranked_result: dict, raw_data: list) -> tuple[dict, float]`
**Purpose**: Execute the filtering step with tracking and logging.

**Returns**: Tuple of (filtered_result, step_time)

**Key detail**: Uses `ranked_result.get("ranked_data") or raw_data` as fallback.

---

#### `execute_contextualize_step(contextualizer, query: str, filtered_result: dict, original_query: str) -> tuple[dict, list, float]`
**Purpose**: Execute the contextualization step with tracking, logging, and fact extraction.

**Returns**: Tuple of (contextualized_result, top_facts, step_time)

**Side effects**:
- Extracts top facts from contextualized data
- Tracks step in tracking system
- Logs step results

---

### Architectural Patterns

1. **Step extraction**: Each pipeline step is a separate function
2. **Consistent returns**: All steps return (result, step_time) tuple
3. **Tracking integration**: Each step calls tracker and logger
4. **Fallback logic**: Filter step falls back to raw_data if ranked_data is empty

---

### Dependencies

**Internal**:
- `services.pipeline.contextualizer_logging`: log_* functions
- `services.pipeline.contextualizer_tracking_steps`: track_* functions
- `services.pipeline.data_contextualizer_utils`: extract_top_facts

---

### Lessons Learned

1. **Extract steps into functions**: Makes pipeline easier to test and debug
2. **Consistent return format**: All steps return (result, time) tuple
3. **Integrated tracking**: Each step tracks and logs itself
4. **Fallback logic**: Handle empty data gracefully

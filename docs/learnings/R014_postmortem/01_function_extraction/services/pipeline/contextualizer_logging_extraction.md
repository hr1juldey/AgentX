# contextualizer_logging.py - Function Extraction

## File: services/pipeline/contextualizer_logging.py

### Primary Purpose
Logging utilities for DATA CONTEXTUALIZER pipeline - extracts metrics and logs step results.

### Key Functions

#### `extract_rerank_metrics(ranked_result: dict, raw_data: list) -> dict`
**Purpose**: Extract rerank metrics for logging.

**Returns**:
- `"Reranked"`: Count of reranked documents
- `"avg score"`: Average relevance score

**Uses**: `safe_get()` and `safe_get_list()` from agent_logging.

---

#### `extract_filter_metrics(filtered_result: dict) -> dict`
**Purpose**: Extract filter metrics for logging.

**Returns**:
- `"Filtered"`: Count of kept documents
- `"removed"`: Number of documents removed

---

#### `extract_contextualize_metrics(contextualized_result: dict, top_facts: list) -> dict`
**Purpose**: Extract contextualize metrics for logging.

**Returns**:
- `"Extracted"`: Number of key facts extracted
- `"from"`: Number of documents processed

---

#### `log_rerank_result(...)`, `log_filter_result(...)`, `log_contextualize_result(...)`
**Purpose**: Log step results with metrics and timing.

**Pattern**: Extract metrics → call `log_step_result()` from agent_logging.

---

### Architectural Patterns

1. **Separation of concerns**: Metric extraction separate from logging
2. **Delegation**: Uses `agent_logging` utilities for actual logging
3. **Consistent format**: All metrics follow same pattern

---

### Dependencies

**Internal**:
- `services.pipeline.agent_logging`: log_step_result, safe_get, safe_get_list

---

### Lessons Learned

1. **Metric extraction should be separate**: Easier to test and modify
2. **Delegate to shared utilities**: Don't duplicate logging logic
3. **Consistent metric format**: All steps should return similar metric dicts

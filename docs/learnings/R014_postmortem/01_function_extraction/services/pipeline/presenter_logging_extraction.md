# presenter_logging.py - Function Extraction

## File: services/pipeline/presenter_logging.py

### Primary Purpose
Logging utilities for PRESENTER pipeline - extracts metrics and logs step results.

### Key Functions

#### `extract_flow_metrics(flow_result: dict) -> dict`
**Purpose**: Extract flow metrics from result.

**Returns**:
- `"Flow"`: flow_analysis (default: "Coherent flow")
- `"Pacing"`: pacing_analysis (default: "Appropriate pacing")
- `"Issues"`: Total count of flow_issues + pacing_issues

---

#### `extract_polish_metrics(polish_result: dict, widgets: list) -> dict`
**Purpose**: Extract polish metrics from result.

**Returns**:
- `"Enhanced"`: Count of enhanced widgets (e.g., "5 widgets")
- `"Suggestions"`: Count of transition suggestions

---

#### `extract_qa_metrics(qa_result: dict) -> dict`
**Purpose**: Extract QA metrics from result.

**Returns**:
- `"Quality"`: quality_check status
- `"Accessibility"`: accessibility_check status
- `"Format"`: format_check status
- `"All passed"`: all_passed boolean

---

#### `log_flow_check_result(...)`, `log_polish_result(...)`, `log_qa_result(...)`
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
- `services.pipeline.agent_logging`: log_step_result, safe_get

---

### Lessons Learned

1. **Metric extraction should be separate**: Easier to test and modify
2. **Delegate to shared utilities**: Don't duplicate logging logic
3. **Consistent metric format**: All steps should return similar metric dicts
4. **Count issues**: Track total issues for quality assessment

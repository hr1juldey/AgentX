# sequencer_logging.py - Function Extraction

## File: services/pipeline/sequencer_logging.py

### Primary Purpose
Logging utilities for SEQUENCER pipeline - extracts narrative flow and pacing data.

### Key Functions

#### `extract_narrative_flow_data(flow_result: dict) -> tuple`
**Purpose**: Extract narrative flow data from result.

**Returns**: Tuple of (narrative_arc, is_valid)

**Defaults**:
- narrative_arc: "hook → context → insight → action"
- is_valid: True

---

#### `extract_pacing_data(pacing_result: dict) -> float`
**Purpose**: Extract pacing data from result.

**Returns**: Total duration as float (default: 0)

---

#### `log_narrative_flow_result(flow_result: dict) -> tuple`
**Purpose**: Log narrative flow result and extract key data.

**Side effect**: Logs "Narrative arc: {arc}"

**Returns**: Tuple of (narrative_arc, is_valid)

---

#### `log_pacing_result(pacing_result: dict, sequence: list) -> float`
**Purpose**: Log pacing result and extract total duration.

**Metrics**:
- "Total duration": "{duration:.1f}s"
- "delivery": "staggered"
- "sequence length": count

**Returns**: Total duration as float

---

### Architectural Patterns

1. **Extraction + logging**: Extract data and log in same function
2. **Default values**: Provide sensible defaults for missing data
3. **Narrative arc tracking**: Follow storytelling structure (hook → context → insight → action)

---

### Dependencies

**Internal**:
- `services.pipeline.agent_logging`: log_step_result, safe_get, logger

---

### Lessons Learned

1. **Narrative structure matters**: Stories have arcs (hook → insight → action)
2. **Pacing is quantifiable**: Total duration helps with UX planning
3. **Defaults are critical**: LLM outputs may be missing fields
4. **Staggered delivery**: Sequence implies staggered, not simultaneous

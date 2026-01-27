# contextualizer_tracking_steps.py - Function Extraction

## File: services/pipeline/contextualizer_tracking_steps.py

### Primary Purpose
Track data flow through each contextualizer step - shows input/output comparisons.

### Key Functions

#### `track_rerank_step(raw_data: list, ranked_result: dict, step_time: float) -> None`
**Purpose**: Track rerank step with input/output comparison.

**Logs**:
- Input document count
- Output document count
- Score count and average
- Top result sample (title)

---

#### `track_filter_step(ranked_data: list, filtered_result: dict, step_time: float) -> None`
**Purpose**: Track filter step with input/output comparison.

**Logs**:
- Input document count
- Output document count
- Removed count
- **Warning** if removal rate > 50%

**Key insight**: High removal rate warning helps detect over-filtering.

---

#### `track_contextualize_step(filtered_data: list, contextualized_result: dict, top_facts: list, step_time: float) -> None`
**Purpose**: Track contextualize step with input/output comparison.

**Logs**:
- Input document count
- Output document count
- Extracted facts count
- Sample facts (first 2)

---

### Architectural Patterns

1. **Input/output comparison**: Show data flow through each step
2. **Warning system**: Detect potential issues (high removal rate)
3. **Sample display**: Show actual data samples for debugging

---

### Dependencies

**Internal**:
- None (standalone)

**External**:
- `logging`: Standard logging

---

### Lessons Learned

1. **Compare input vs output**: Shows if step is losing too much data
2. **Warn on anomalies**: High removal rate > 50% needs attention
3. **Show samples**: Actual data samples help debug quality issues
4. **Track timing**: step_time parameter available for performance analysis

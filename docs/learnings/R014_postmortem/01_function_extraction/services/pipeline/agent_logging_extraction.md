# agent_logging.py - Function Extraction

## File: services/pipeline/agent_logging.py

### Primary Purpose
Unified logging infrastructure for all pipeline agents - shared utilities.

### Key Functions

#### `safe_get(result: Any, key: str, default: Any = None) -> Any`
**Purpose**: Safely retrieve values from potentially non-dict objects.

**Returns**: `result.get(key, default)` if has get method, else default.

**Use case**: Handle DSPy coroutines that look like dicts but aren't.

---

#### `safe_get_list(result: Any, key: str) -> List[Any]`
**Purpose**: Safely retrieve lists from potentially non-dict objects.

**Returns**: `result.get(key, [])` if has get method, else empty list.

---

#### `log_step_start(agent_name: str, step_name: str, detail: str = "") -> None`
**Purpose**: Log the start of a pipeline step.

**Format**: `[{agent_name}] {step_name} {detail}...` or `[{agent_name}] {step_name}...`

---

#### `log_step_result(step_name: str, metrics: dict[str, Any], step_time: float) -> None`
**Purpose**: Log the result of a pipeline step with timing.

**Format**: `→ {step_name}: {metric_str} ({step_time:.2f}s)`

**Metric str**: Comma-separated `key: value` pairs.

---

### Architectural Patterns

1. **Safe extraction**: Handle both dicts and non-dicts
2. **Consistent logging format**: All agents use same log format
3. **Timing integration**: Step timing built into logging

---

### Dependencies

**Internal**:
- None (standalone utilities)

**External**:
- `logging`: Standard logging
- `typing`: Type hints

---

### Lessons Learned

1. **Safe get is critical**: DSPy coroutines require hasattr() checks
2. **Consistent log format**: Makes logs easier to parse
3. **Include timing**: Performance data is essential for debugging
4. **Shared utilities**: Don't duplicate logging code across agents

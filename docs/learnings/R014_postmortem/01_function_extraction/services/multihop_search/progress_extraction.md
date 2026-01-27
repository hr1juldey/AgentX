# progress.py - Function Extraction

## File: services/multihop_search/execution/progress.py

### Primary Purpose
Progress tracking and event sending for hop execution.

### Key Classes

#### `HopProgressTracker`
**Purpose**: Tracks and sends progress updates during hop execution.

**Init parameters**:
- `progress_callback`: Callback for progress updates
- `max_hops`: Maximum number of hops

---

### Key Methods

#### `send_hop_start(hop_number: int, strategy: str, search_query: str)`
**Purpose**: Send hop start event.

**Progress**: `(hop_number - 1) / max_hops`

**Event type**: "hop_start"

---

#### `send_documents_found(hop_number: int, results_count: int)`
**Purpose**: Send documents found event.

**Progress**: `(hop_number - 0.7) / max_hops`

**Event type**: "hop_progress"

**Message**: "Found {results_count} documents"

---

#### `send_assessing(hop_number: int)`
**Purpose**: Send assessing completeness event.

**Progress**: `(hop_number - 0.4) / max_hops`

**Event type**: "hop_progress"

**Message**: "Assessing completeness..."

---

#### `send_complete(hop_number: int, reasoning: str)`
**Purpose**: Send hop complete event.

**Progress**: `1.0`

**Event type**: "hop_complete"

**Includes**: Reflection reasoning

---

### Architectural Patterns

1. **Progress tracking class**: Encapsulates progress logic
2. **Event-based communication**: Sends events via callback
3. **Granular progress**: Multiple events per hop (start, found, assessing, complete)

---

### Dependencies

**Internal**:
- `services.multihop_search.execution.hop_helpers`: send_progress_event

**External**:
- `typing`: Type hints

---

### Lessons Learned

1. **Granular progress updates**: Multiple events per hop improve UX
2. **Progress percentages**: Calculate relative to hop position
3. **Reasoning in events**: Include reflection reasoning for transparency
4. **Event-driven architecture**: Callbacks enable WebSocket streaming

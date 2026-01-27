# hop_helpers.py - Function Extraction

## File: services/multihop_search/execution/hop_helpers.py

### Primary Purpose
Shared helper functions for multi-hop search execution.

### Key Functions

#### `send_progress_event(...)`
**Purpose**: Send progress update via callback.

**Parameters**:
- `callback`: Progress callback function
- `event_type`: Event type string
- `hop_number`, `total_hops`: Hop tracking
- `message`: Human-readable message
- `progress`: Progress float (0-1)
- `eta_seconds`: Optional ETA
- `documents_found`: Document count
- `query_used`: Search query used
- `reflection_reasoning`: Reflection output

**Creates**: HopEvent object and calls callback.

---

#### `summarize_documents(documents: list[SearchResultItem]) -> str`
**Purpose**: Create brief summary for assessment.

**Logic**:
- Returns "No documents found." if empty
- Summarizes first 5 documents (title + 150 chars of content)

**Returns**: String summary with numbered items.

---

#### `build_search_context(results: list[Any]) -> str`
**Purpose**: Build context string from search results.

**Format**: `[1] {title}\n{content}\n\n[2] ...`

---

#### `generate_search_query(question: str, hop_num: int, plan_result: Any) -> tuple[str, str]`
**Purpose**: Generate search query for this hop.

**Logic**:
- Hop 1: Use original question, strategy "INITIAL"
- Hop 2+: Use plan_result.next_query and plan_result.strategy
- Fallback: `"{question} details"`, strategy "REFINE_TOPIC"

**Returns**: Tuple of (search_query, strategy).

---

#### `generate_hop_answer(answer_module: dspy.ChainOfThought, question: str, context: str) -> str`
**Purpose**: Generate answer for current hop context.

**Calls**: `answer_module(question=question, context=context)`

**Returns**: Generated answer string.

---

### Architectural Patterns

1. **Progress tracking**: Send events via callback for UI updates
2. **Context building**: Format results for LLM consumption
3. **Strategy pattern**: Different query generation per hop number
4. **Answer generation**: Use DSPy ChainOfThought for synthesis

---

### Dependencies

**Internal**:
- `services.multihop_search.schemas`: HopEvent
- `services.multihop_search.search_client`: SearchResultItem

**External**:
- `dspy`: DSPy framework
- `typing`: Type hints

---

### Lessons Learned

1. **Progress callbacks enable streaming**: UI updates happen in real-time
2. **Context formatting matters**: LLM needs structured context
3. **Hop-based strategies**: First hop uses original query, later hops refine
4. **Summarization for assessment**: Brief summaries help LLM assess completeness

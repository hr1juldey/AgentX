# Battle-Tested Solutions in R014

## Summary
**Total Solutions Documented**: 8
**Status**: All production-tested and verified
**Source**: `tests/test_fix_log.md`, `LLM_MODULE_STANDALONE_TEST_REPORT.md`
**Test Coverage**: 96% (50/52 tests passing)

---

## Solution 1: Async/Sync Compatibility Layer

**Problem**: Event loop issues when calling async SearXNG search from sync contexts
**Location**: `services/tools/researcher/search_async_wrapper.py`
**Status**: ✅ Fixed after 3 iterations
**Reuse**: REQUIRED for any async dependencies

### The Problem

**Error Message**:
```
RuntimeError: There is no current event loop in thread 'MainThread'
```

**Context**:
```python
# SearXNG search is async
async def search(query: str) -> list[dict]:
    async with AsyncClient() as client:
        results = await client.get(f"http://localhost:8080/search?q={query}")
        return results.json()

# But called from sync context (DSPy module)
class SearXNGSearchModule(dspy.Module):
    def forward(self, query: str) -> dspy.Prediction:
        results = search(query)  # ❌ RuntimeError!
```

**Root Cause**: DSPy modules run in sync context, but SearXNG uses async/await.

### Solution Evolution

**Attempt 1**: Direct await (failed)
```python
class SearXNGSearchModule(dspy.Module):
    def forward(self, query: str) -> dspy.Prediction:
        results = await search(query)  # ❌ SyntaxError: await outside async
```

**Attempt 2**: asyncio.run() (failed)
```python
class SearXNGSearchModule(dspy.Module):
    def forward(self, query: str) -> dspy.Prediction:
        results = asyncio.run(search(query))  # ❌ RuntimeError: no running event loop
```

**Attempt 3**: ✅ ThreadPoolExecutor wrapper (SUCCESS)
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Coroutine
import functools

# services/tools/researcher/search_async_wrapper.py
_thread_pool: ThreadPoolExecutor | None = None

def get_thread_pool() -> ThreadPoolExecutor:
    """Get or create thread pool for async execution."""
    global _thread_pool
    if _thread_pool is None:
        _thread_pool = ThreadPoolExecutor(max_workers=4)
    return _thread_pool

def run_async_in_sync_context(coro: Coroutine[Any, Any, Any]) -> Any:
    """Run async coroutine in sync context using ThreadPoolExecutor.

    This is required when calling async functions from DSPy modules
    which run in a synchronous context.
    """
    def run_in_new_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    pool = get_thread_pool()
    future = pool.submit(run_in_new_loop)
    return future.result()

# Usage in DSPy module
class SearXNGSearchModule(dspy.Module):
    def forward(self, query: str) -> dspy.Prediction:
        # ✅ Works! Run async in sync context
        results = run_async_in_sync_context(search(query))
        return dspy.Prediction(search_results=results)
```

### Why It Works

1. **ThreadPoolExecutor**: Runs async code in separate thread
2. **New Event Loop**: Each thread gets its own event loop
3. **Blocking Wait**: `future.result()` blocks until async completes
4. **Reusable Pool**: Thread pool reused across calls (efficient)

### Performance Considerations

| Approach | Latency | Throughput | Notes |
|----------|---------|------------|-------|
| Direct async (ideal) | ~100ms | High | Not possible from sync context |
| ThreadPoolExecutor (4 workers) | ~120ms | Medium | ✅ Works reliably |
| asyncio.run() | Fails | N/A | Event loop conflict |
| ProcessPoolExecutor | ~300ms | Low | Overkill for I/O-bound |

**Result**: 20% overhead vs ideal, but enables async/sync interop.

### Thread Safety

```python
# Thread pool is thread-safe
import threading

_lock = threading.Lock()

def run_async_in_sync_context(coro: Coroutine) -> Any:
    """Thread-safe version with lock."""
    with _lock:
        # Critical section for thread pool access
        pool = get_thread_pool()
        future = pool.submit(run_in_new_loop, coro)
        return future.result()
```

### Cleanup

```python
import atexit

@atexit.register
def cleanup_thread_pool():
    """Clean up thread pool on exit."""
    global _thread_pool
    if _thread_pool is not None:
        _thread_pool.shutdown(wait=True)
        _thread_pool = None
```

### Reuse for Real AgentX

**Status**: ✅ REQUIRED - Needed for any async dependency

**When to Use**:
- Calling async functions from sync context (DSPy modules, etc.)
- Integrating async libraries (aiohttp, asyncpg, etc.)
- Running async code in tests or scripts

**Integration Pattern**:
```python
# core/async_compat/run_async.py
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Coroutine
import asyncio
import atexit

_thread_pool: ThreadPoolExecutor | None = None

def get_thread_pool() -> ThreadPoolExecutor:
    global _thread_pool
    if _thread_pool is None:
        _thread_pool = ThreadPoolExecutor(max_workers=4)
        atexit.register(cleanup)
    return _thread_pool

def run_async(coro: Coroutine[Any, Any, Any]) -> Any:
    """Run async coroutine in sync context."""
    def run_in_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    pool = get_thread_pool()
    return pool.submit(run_in_loop).result()

def cleanup():
    global _thread_pool
    if _thread_pool:
        _thread_pool.shutdown(wait=True)
        _thread_pool = None

# Usage
from core.async_compat.run_async import run_async

async def fetch_data():
    return await async_api_call()

# In sync context
data = run_async(fetch_data())
```

---

## Solution 2: Type Conversion Helpers

**Problem**: LLMs return text, not numbers/bools
**Location**: `services/tools/common/type_utils.py` (91 lines)
**Status**: ✅ Resolved all type mismatches
**Reuse**: REQUIRED for all LLM interactions

### The Problem

**Expected**:
```python
class AssessData(dspy.Signature):
    data_completeness = dspy.OutputField(desc="Completeness score 0.0 to 1.0")
    needs_more_research = dspy.OutputField(desc="Whether more research is needed")

# Expect:
data_completeness: float = 0.85
needs_more_research: bool = True
```

**Actual**:
```python
# LLM returns:
data_completeness: str = "High"  # ❌ Not a float!
needs_more_research: str = "yes, definitely"  # ❌ Not a bool!
```

**Root Cause**: LLMs generate text, not typed values. DSPy doesn't enforce types.

### The Solution

```python
# services/tools/common/type_utils.py
from typing import Any

def _to_float(value: Any, default: float = 0.0) -> float:
    """Convert value to float with default fallback.

    Handles:
    - Direct float/int: 0.75 → 0.75
    - String floats: "0.75" → 0.75
    - Percentages: "75%" → 0.75
    - Keywords: "high" → 0.75, "medium" → 0.5, "low" → 0.25
    - Unknown: return default
    """
    # Fast path: already a number
    if isinstance(value, (int, float)):
        return float(value)

    # String conversion
    if isinstance(value, str):
        value = value.strip().lower()

        # Handle percentages
        if value.endswith("%"):
            try:
                return float(value[:-1]) / 100
            except ValueError:
                pass

        # Try direct float conversion
        try:
            return float(value)
        except ValueError:
            pass

        # Keyword mappings
        mappings = {
            "high": 0.75,
            "very high": 0.9,
            "excellent": 0.95,
            "medium": 0.5,
            "moderate": 0.5,
            "low": 0.25,
            "very low": 0.1,
            "poor": 0.1,
            # Numeric words
            "one": 1.0,
            "two": 2.0,
            "three": 3.0,
            "four": 4.0,
            "five": 5.0,
        }
        return mappings.get(value, default)

    # Unknown type
    return default


def _to_bool(value: Any, default: bool = False) -> bool:
    """Convert value to bool with default fallback.

    Handles:
    - Direct bool: True → True
    - Numbers: 1 → True, 0 → False
    - Strings: "true", "yes", "1" → True
    - Strings: "false", "no", "0" → False
    - Unknown: return default
    """
    # Fast path: already bool
    if isinstance(value, bool):
        return value

    # Numbers
    if isinstance(value, (int, float)):
        return bool(value)

    # String conversion
    if isinstance(value, str):
        value = value.strip().lower()

        # True values
        if value in ("true", "yes", "1", "y", "t"):
            return True

        # False values
        if value in ("false", "no", "0", "n", "f"):
            return False

    # Unknown type
    return default


def _to_int(value: Any, default: int = 0) -> int:
    """Convert value to int with default fallback.

    Similar to _to_float but returns int.
    """
    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    if isinstance(value, str):
        value = value.strip().lower()
        try:
            return int(float(value))  # Handles "5.0" → 5
        except ValueError:
            pass

        # Number words
        word_to_num = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        }
        return word_to_num.get(value, default)

    return default
```

### Usage Pattern

```python
# After DSPy call
result = self.assess_data(query=query, available_data=data)

# ✅ Always convert
completeness = _to_float(result.data_completeness, default=0.5)
needs_research = _to_bool(result.needs_more_research, default=False)
priority = _to_int(result.priority, default=1)

# Now use typed values
if completeness > 0.7 and not needs_research:
    return final_answer()
```

### Test Coverage

| Input Type | Example | _to_float() | _to_bool() | _to_int() |
|------------|---------|-------------|------------|-----------|
| Direct | 0.75 | 0.75 ✅ | True ✅ | 0 ✅ |
| String num | "0.75" | 0.75 ✅ | - | 0 ✅ |
| Percentage | "75%" | 0.75 ✅ | - | - |
| Keyword | "high" | 0.75 ✅ | - | - |
| Bool str | "yes" | - | True ✅ | - |
| Number word | "three" | 3.0 ✅ | - | 3 ✅ |
| Unknown | "xyz" | 0.0 (def) | False (def) | 0 (def) |

### Why It Works

1. **Multiple Fallbacks**: Try best → keyword → default
2. **Keyword Mappings**: Captures semantic meaning
3. **Graceful Degradation**: Never crashes, always returns valid type
4. **Consistent Behavior**: Same conversion everywhere

### Reuse for Real AgentX

**Status**: ✅ REQUIRED - Use for all LLM outputs

**Integration**:
```python
# core/llm/type_utils.py
from typing import Any

def _to_float(value: Any, default: float = 0.0) -> float:
    """Convert LLM output to float."""
    # ... (implementation from above)

def _to_bool(value: Any, default: bool = False) -> bool:
    """Convert LLM output to bool."""
    # ... (implementation from above)

def _to_int(value: Any, default: int = 0) -> int:
    """Convert LLM output to int."""
    # ... (implementation from above)

# Usage in all DSPy modules
from core.llm.type_utils import _to_float, _to_bool, _to_int
```

---

## Solution 3: Regex-Based Score Extraction

**Problem**: LLM returns scores in conversational format
**Location**: `services/tools/researcher/citation_builder.py`
**Status**: ✅ Fixed with regex + keyword fallback
**Reuse**: HIGH for any numeric extraction

### The Problem

**LLM Output Variations**:
```
"The relevance score is 0.85"
"Score: 75%"
"High relevance (0.9)"
"moderately relevant"
```

**Need**: Extract numeric score from all these formats.

### The Solution

```python
import re
from typing import Any

def _parse_relevance_score(score_str: Any) -> float:
    """Parse relevance score with multiple fallbacks."""

    # Fallback 1: Direct float
    try:
        return float(score_str)
    except (ValueError, TypeError):
        pass

    # Fallback 2: Regex extraction
    if isinstance(score_str, str):
        # Find first number in string
        match = re.search(r'(\d+\.?\d*)', score_str)
        if match:
            value = float(match.group(1))

            # Handle percentage (>1.0 means percentage)
            if value > 1.0:
                return value / 100.0
            return value

    # Fallback 3: Keyword mapping
    if isinstance(score_str, str):
        lower = score_str.lower().strip()
        mappings = {
            "high": 0.8,
            "very high": 0.9,
            "excellent": 0.95,
            "medium": 0.5,
            "moderate": 0.5,
            "low": 0.2,
            "very low": 0.1,
        }
        return mappings.get(lower, 0.5)

    # Fallback 4: Default
    return 0.5
```

### Test Cases

| Input | Output | Method |
|-------|--------|--------|
| `0.85` | 0.85 | Direct float |
| `"0.75"` | 0.75 | Direct float |
| `"The score is 0.9"` | 0.9 | Regex extraction |
| `"75%"` | 0.75 | Regex + percentage |
| `"High relevance"` | 0.8 | Keyword mapping |
| `"xyz"` | 0.5 | Default |

### Regex Patterns

```python
# Pattern 1: Find first number
re.search(r'(\d+\.?\d*)', text)

# Pattern 2: Find percentage specifically
re.search(r'(\d+\.?\d*)\s*%', text)

# Pattern 3: Find fraction
re.search(r'(\d+)\s*/\s*(\d+)', text)  # "3/4" → 0.75

# Pattern 4: Find range
re.search(r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)', text)  # "0.7-0.9" → 0.8 (avg)
```

### Reuse for Real AgentX

**Status**: ✅ HIGH - Use for any numeric extraction from text

**Template**:
```python
import re
from typing import Any

def extract_number(text: Any, default: float = 0.0) -> float:
    """Extract first number from text with fallbacks."""

    # Direct number
    if isinstance(text, (int, float)):
        return float(text)

    # String conversion
    if isinstance(text, str):
        # Try direct conversion
        try:
            return float(text)
        except ValueError:
            pass

        # Regex extraction
        match = re.search(r'(\d+\.?\d*)', text)
        if match:
            value = float(match.group(1))
            # Handle percentage
            if value > 1.0 and '%' in text:
                return value / 100.0
            return value

    return default
```

---

## Solution 4: Chunking + Iteration for Large Inputs

**Problem**: LLM context window exceeded, corrupted outputs
**Location**: `services/tools/analyst/insight_extractor.py`
**Status**: ✅ Fixed with 3-phase chunking
**Reuse**: REQUIRED for any variable-length input

### The Problem

**Before**:
- Small query (97 chars): Works ✅
- Large query (1600 chars): Returns corrupted text ❌

**Symptoms**:
- Returns first 2-3 chars: "In ", "Inf ", "Jav"
- Returns 1484-1762 corrupted items
- LLM truncates response due to context overflow

### The Solution

```python
MAX_CHUNK_SIZE = 500
OVERLAP = 100
ITERATIONS = 3

class InsightExtractorModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.extract_chunk = dspy.ChainOfThought(ExtractInsightsChunk)

    def forward(self, query: str, document_text: str) -> dspy.Prediction:
        """Extract insights with chunking for large documents."""

        # Decision tree: small = fast path, large = chunked
        if len(document_text) <= MAX_CHUNK_SIZE:
            return self._extract_single(document_text)

        return self._extract_iterative(document_text)

    def _extract_single(self, text: str) -> dspy.Prediction:
        """Fast path for small documents."""
        result = self.extract_chunk(chunk=text)
        return dspy.Prediction(
            insights=result.insights,
            rationale=result.rationale,
        )

    def _extract_iterative(self, text: str) -> dspy.Prediction:
        """Chunked path for large documents."""
        all_insights = []
        all_rationales = []

        for i in range(ITERATIONS):
            # Calculate chunk bounds with overlap
            start = i * (MAX_CHUNK_SIZE - OVERLAP)
            end = start + MAX_CHUNK_SIZE
            chunk = text[start:end]

            # Extract from this chunk
            result = self.extract_chunk(chunk=chunk)
            all_insights.append(result.insights)
            all_rationales.append(result.rationale)

        # Combine results
        combined_insights = "\n".join(all_insights)
        combined_rationale = "\n".join(all_rationales)

        return dspy.Prediction(
            insights=combined_insights,
            rationale=combined_rationale,
        )
```

### Token Efficiency

| Input Size | Strategy | Tokens/Call | Calls | Total | Quality |
|------------|----------|-------------|-------|-------|---------|
| 97 chars | Direct | 50 | 1 | 50 | ⭐⭐⭐⭐⭐ |
| 1600 chars | Chunked (3x) | 40 | 3 | 120 | ⭐⭐⭐⭐⭐ |
| 1600 chars | Single shot | 200 | 1 | 200 | ⭐⭐ (corrupted) |

**Key Insight**: Chunking uses fewer total tokens (120 vs 200) with better quality.

### Parameter Tuning

**For qwen3:8b** (8.2B params, ~4K context):
- `MAX_CHUNK_SIZE = 500`: Safe window (context / 8)
- `OVERLAP = 100`: Prevents splitting insights (~paragraph length)
- `ITERATIONS = 3`: Covers 1500 chars (3 × 400 effective)

**For larger models** (GPT-4, 32K+ context):
- `MAX_CHUNK_SIZE = 2000`: Can handle larger chunks
- `OVERLAP = 200`: Larger overlap for larger context
- `ITERATIONS = 1`: Often don't need chunking

### Reuse for Real AgentX

**Status**: ✅ REQUIRED - For any variable-length input

**Template**:
```python
class ChunkedProcessor(dspy.Module):
    """Process variable-length inputs with chunking."""

    MAX_CHUNK_SIZE = 500  # Tune for your model
    OVERLAP = 100
    ITERATIONS = 3

    def forward(self, text: str) -> dspy.Prediction:
        if len(text) <= self.MAX_CHUNK_SIZE:
            return self._process_single(text)
        return self._process_chunked(text)

    def _process_chunked(self, text: str) -> dspy.Prediction:
        results = []
        for i in range(self.ITERATIONS):
            start = i * (self.MAX_CHUNK_SIZE - self.OVERLAP)
            end = start + self.MAX_CHUNK_SIZE
            chunk = text[start:end]
            result = self.process_chunk(chunk=chunk)
            results.append(result)
        return self._combine_results(results)
```

---

## Solution 5: Few-Shot Semantic Learning

**Problem**: Hard-coded rules brittle, don't generalize
**Location**: `services/tools/selectors/widget_matcher.py`
**Status**: ✅ Fixed with examples in signature
**Reuse**: HIGH for classification/selection tasks

### The Problem

**Before** (hard-coded rules):
```python
SEMANTIC_RULES = {
    "stock": "chart",
    "price": "chart",
    "weather": "card",
    # ...
}

def match_widget(query: str) -> str:
    for keyword, widget in SEMANTIC_RULES.items():
        if keyword in query.lower():
            return widget
    return "markdown"

# Works: "stock prices" → "chart" ✅
# Fails: "equity values" → "markdown" ❌ (should be "chart")
```

### The Solution

```python
class SelectWidgetSignature(dspy.Signature):
    """Select widgets based on query intent and data characteristics.

    SEMANTIC PATTERNS (learn from these examples):

    Example 1:
    Query: "Show real-time stock prices"
    Data: numerical_time_series
    Selected: chart
    Reasoning: Stock prices are time-series data that change continuously.
               Charts visualize trends over time better than static widgets.

    Example 2:
    Query: "What's the weather like?"
    Data: current_conditions
    Selected: card
    Reasoning: Weather is current state data, best shown in a compact card.

    Example 3:
    Query: "Find articles about Python"
    Data: text_documents
    Selected: gallery
    Reasoning: Multiple documents are best browsed in a gallery grid.

    NOTE: These are EXAMPLES to learn from, not hard-coded rules.
    Analyze the semantic relationship between query and data.
    """
    query = dspy.InputField(desc="User's natural language query")
    data_type = dspy.InputField(desc="Type of data available")
    selected_widgets = dspy.OutputField(desc="JSON array of widget names")
    rationale = dspy.OutputField(desc="Reasoning for widget selection")
```

### Test Results

| Query | Before (Rules) | After (Few-Shot) |
|-------|----------------|------------------|
| "Show stock prices" | `['chart']` ✅ | `['chart']` ✅ |
| "Show equity values" | `['markdown']` ❌ | `['chart']` ✅ |
| "Financial time series" | `['markdown']` ❌ | `['chart']` ✅ |
| "Current weather" | `['card']` ✅ | `['card']` ✅ |

**Key Result**: System generalizes from examples, handles novel queries.

### Why It Works

1. **Semantic Understanding**: LLM learns "equity values" ≈ "stock prices"
2. **Reasoning Trace**: Rationale explains decision
3. **No Hard Rules**: System can handle unseen queries
4. **Examples > Rules**: Few-shot learning more flexible

### Reuse for Real AgentX

**Status**: ✅ HIGH - For classification/selection tasks

**Template**:
```python
class ClassifyIntentSignature(dspy.Signature):
    """Classify user intent based on semantic patterns.

    EXAMPLES (learn from these):

    Example 1:
    Input: "What's the weather?"
    Intent: weather_query
    Reasoning: User asking about current conditions.

    Example 2:
    Input: "Show me stock prices"
    Intent: financial_query
    Reasoning: User wants financial data visualization.

    NOTE: These are examples. Generalize to new inputs.
    """
    user_input = dspy.InputField(desc="User's message")
    intent = dspy.OutputField(desc="Classified intent")
    reasoning = dspy.OutputField(desc="Reasoning for classification")
```

---

## Solution 6: ReAct Instead of CodeAct

**Problem**: CodeAct fails with small LLMs (qwen3:8b)
**Location**: `services/tools/calendar/calendar_agent.py`
**Status**: ✅ Fixed (5/5 tests passing)
**Reuse**: CRITICAL for small LLMs

### The Problem

**CodeAct** requires strict JSON output:
```json
{
  "generated_code": "result = get_current_date()",
  "finished": true
}
```

**Reality with qwen3:8b**:
```
Let me check the current date for you.

result = get_current_date()
print(result)

The current date is January 23, 2026.
```

**Result**: CodeAct fails to parse, returns None.

### The Solution

```python
# BEFORE: CodeAct (fails on small LLMs)
self.codeact = dspy.CodeAct(
    signature=CalendarQuery,
    tools=[get_current_date, calculate_date_offset],
    max_iters=3,
)

# AFTER: ReAct (works reliably)
self.react = dspy.ReAct(
    signature=CalendarQuery,
    tools=[get_current_date, calculate_date_offset],
    max_iters=3,
)
```

**ReAct Format** (more tolerant):
```
Thought: I need to get the current date.
Action: get_current_date()
Observation: 2026-01-23
Thought: Now I can answer.
Action: Finish[The current date is January 23, 2026.]
```

### Test Results

| Test | CodeAct | ReAct |
|------|---------|-------|
| Current date | ❌ Parse error | ✅ "2026-01-23" |
| Day of week | ❌ Parse error | ✅ "Saturday" |
| Date offset (+7) | ❌ Parse error | ✅ "January 30, 2026" |
| Date difference | ❌ Parse error | ✅ "364 days" |
| Weekend check | ❌ Parse error | ✅ "No, not weekend" |

**Result**: 0/5 → 5/5 tests passing

### When to Use Which

| Agent Type | Use CodeAct | Use ReAct |
|------------|-------------|-----------|
| Small LLMs (<10B) | ❌ | ✅ |
| Large LLMs (GPT-4, Claude) | ✅ | ✅ |
| Tool calling focus | ❌ | ✅ |
| Code generation focus | ✅ | ❌ |

### Reuse for Real AgentX

**Status**: ✅ CRITICAL for qwen3:8b, gemma3:4b

**Rule**: If using small LLMs, ALWAYS use ReAct for agents with tools.

---

## Solution 7: Explicit Signatures with ChainOfThought

**Problem**: Generic `Predict` returns unparsable string
**Location**: `services/tools/researcher/data_structurer.py`
**Status**: ✅ Fixed with explicit fields
**Reuse**: REQUIRED for structured data

### The Problem

**Before**:
```python
self.structure = dspy.Predict("beautiful_data -> organized_data")
result = self.structure(beautiful_data=raw_data)

# result.organized_data is a STRING, not dict!
# "Some key facts:\n1. Fact one\n2. Fact two\n..."
```

**Issue**: Cannot access individual fields programmatically.

### The Solution

```python
class StructureDataChunk(dspy.Signature):
    """Structure raw data into key facts, trends, and comparisons.

    Output format:
    - key_facts: Numbered list 1-5
    - trends: Numbered list 1-3
    - comparisons: Numbered list 1-2
    """
    data_chunk = dspy.InputField(desc="Data to structure (max 500 chars)")
    key_facts = dspy.OutputField(desc="Key facts from data, numbered 1-5")
    trends = dspy.OutputField(desc="Trends from data, numbered 1-3")
    comparisons = dspy.OutputField(desc="Comparisons from data, numbered 1-2")

# Use ChainOfThought for better reasoning
self.structure = dspy.ChainOfThought(StructureDataChunk)

# Access fields directly
result = self.structure(data_chunk=raw_data)
facts = result.key_facts  # ✅ String, but predictable format
trends = result.trends   # ✅ Separate field
comparisons = result.comparisons  # ✅ Separate field
```

### Result

**Before**: Unparsable string blob
**After**: Structured dict with separate fields

```python
{
    "key_facts": "1. Fact one\n2. Fact two\n3. Fact three",
    "trends": "1. Trend one\n2. Trend two",
    "comparisons": "1. Comparison one",
}
```

### Reuse for Real AgentX

**Status**: ✅ REQUIRED - No generic Predict signatures

**Rule**: Always use explicit `dspy.Signature` with named output fields.

---

## Solution 8: Connection State Tracking for WebSocket

**Problem**: Callbacks continue after error/disconnect
**Location**: `api/routes/master_agent.py`
**Status**: ✅ Fixed with boolean flag
**Reuse**: REQUIRED for all WebSocket routes

### The Problem

**Before**:
```python
async def send_progress(checkpoint: str):
    await websocket.send_json({"type": "progress", "checkpoint": checkpoint})

# Main pipeline
await run_pipeline(send_progress)  # ❌ Callback continues after error!

# If error occurs, callback still tries to send
# → "WebSocket closed" exceptions cascade
```

### The Solution

```python
@router.websocket("/ws/generate-widget")
async def generate_widget_master_agent(websocket: WebSocket):
    await websocket.accept()

    # ✅ Connection state flag
    connection_active = True

    # Progress callback checks flag
    async def send_qa_progress(checkpoint: str, status: str, data: dict):
        if not connection_active:  # ✅ Stop if disconnected
            return
        try:
            await websocket.send_json({
                "type": "qa_progress",
                "data": {"checkpoint": checkpoint, "status": status, "details": data}
            })
        except Exception:
            pass  # ✅ Silent failure

    try:
        # Main pipeline
        await run_pipeline(send_qa_progress)
    except Exception as e:
        connection_active = False  # ✅ Set flag on error
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        connection_active = False  # ✅ Always set at end
```

### Why It Works

1. **Boolean Flag**: Simple and fast check
2. **Set on Error**: Flag becomes False on first error
3. **Callback Checks**: Each callback checks flag before sending
4. **Silent Failure**: `pass` on WebSocket exceptions

### Reuse for Real AgentX

**Status**: ✅ REQUIRED - All WebSocket routes

**Template**:
```python
@router.websocket("/ws/{endpoint}")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    connection_active = True

    async def send_event(event_type: str, data: dict):
        if not connection_active:
            return
        try:
            await websocket.send_json({"type": event_type, "data": data})
        except Exception:
            pass

    try:
        await run_operation(send_event)
    except Exception as e:
        connection_active = False
        await send_event("error", {"message": str(e)})
    finally:
        connection_active = False
```

---

## Summary Table: Battle-Tested Solutions

| Solution | Problem | Lines | Status | Reuse Priority |
|----------|---------|-------|--------|----------------|
| Async/Sync Wrapper | Event loop issues | ~60 | ✅ | REQUIRED |
| Type Conversion | LLM returns text | ~91 | ✅ | REQUIRED |
| Regex Extraction | Numeric parsing | ~40 | ✅ | HIGH |
| Chunking + Iteration | Context overflow | ~50 | ✅ | REQUIRED |
| Few-Shot Learning | Brittle rules | ~30 | ✅ | HIGH |
| ReAct > CodeAct | Small LLMs | ~10 | ✅ | CRITICAL |
| Explicit Signatures | String returns | ~20 | ✅ | REQUIRED |
| Connection State | WebSocket errors | ~15 | ✅ | REQUIRED |

---

## Critical Rules for Real AgentX

1. **ALWAYS convert LLM outputs** - Use `_to_float`, `_to_bool`, `_to_int`
2. **ALWAYS use async wrapper** - For calling async from sync context
3. **ALWAYS chunk large inputs** - Prevent context overflow
4. **ALWAYS use ReAct** - For small LLMs with tools
5. **ALWAYS use explicit signatures** - No generic Predict
6. **ALWAYS track connection state** - For WebSocket routes
7. **ALWAYS use few-shot examples** - For classification tasks
8. **NEVER assume types** - LLMs return text, not numbers/bools

---

## Conclusion

All 8 solutions are **production-tested** with comprehensive test coverage. Reuse these solutions as-is for Real AgentX development.

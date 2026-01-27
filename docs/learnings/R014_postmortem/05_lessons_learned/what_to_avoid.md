# What to Avoid in Real AgentX

## Summary
**Total Anti-Patterns Documented**: 22
**Categories**: Architecture, DSPy, Code Quality, Integration
**Source**: R014 mistakes + fixes

---

## 1. Verbose DSPy Field Descriptions

**Anti-Pattern**: 50+ word field descriptions with instructions
**Impact**: Medium - LLM confusion, poor performance
**Source**: `services/tools/hydrators/chart_signatures.py` (before fix)

### The Problem

```python
# ❌ WRONG - Verbose field description
class ExtractDocumentNumbers(dspy.Signature):
    document_text = dspy.InputField(desc="Document content to extract numbers from")
    structured_numbers = dspy.OutputField(
        desc="JSON array of extracted numbers. Each entry must have: "
        "label (entity name), value (MUST be numeric float/int, not text), "
        "unit (%, $, billion, million, etc.), context (what the number represents), "
        "year (if available, string like '2023'). "
        "CRITICAL: value field MUST be a number. Skip entries like '1970s_level', 'N/A', 'unknown'. "
        "Example: [{'label': 'US', 'value': 3.7, 'unit': '%', 'context': 'inflation rate', 'year': '2023'}]. "
        "Return ONLY numeric values explicitly found in text. Do not make up values."
    )
```

**Issues**:
- Field description has 50+ words
- Instructions buried in field desc instead of docstring
- LLM has to process verbose text
- Mixes "what it IS" with "HOW to process it"

### The Fix

```python
# ✅ CORRECT - Instructions in docstring, field describes WHAT IT IS
class ExtractDocumentNumbers(dspy.Signature):
    """Extract all numerical data points from document text for chart/table visualization.

    Each extracted number must have a numeric value (int or float).
    Skip non-numeric entries like 'N/A', 'unknown', or text labels.
    Include units (%, $, billion, million) and temporal context (year) when available.
    Return only numbers explicitly found in the text.
    """

    document_text = dspy.InputField(desc="Document content to extract numbers from")
    document_title = dspy.InputField(desc="Document title for context")
    query = dspy.InputField(desc="Research query for context")

    structured_numbers = dspy.OutputField(
        desc="JSON array of extracted numbers with label, numeric value, unit, context, and year"
    )
```

**Benefits**:
- Class docstring contains instructions (task, constraints, what to skip)
- Field description ONLY describes what the field IS
- Clearer for LLM to understand
- Easier to maintain

**Rule**: Instructions in docstring, field desc describes WHAT IT IS (5-10 words max).

---

## 2. Generic Signatures Without Context

**Anti-Pattern**: Extract all data without query context
**Impact**: High - Wrong data extracted
**Source**: `services/tools/hydrators/chart_signatures.py:12-26` (before fix)

### The Problem

```python
# ❌ WRONG - No query context
class ExtractDocumentNumbers(dspy.Signature):
    """Extract all numerical data points from document text."""
    document_text = dspy.InputField(desc="Document content")
    structured_numbers = dspy.OutputField(desc="JSON array of numbers")
```

**Real-World Impact**:
- Query: "Economic Impact of Major Wars Since 2000"
- Extracted: Agricultural Raw Materials Index: 81.29, Beverage Price Index: 207.95
- Should extract: Iraq war cost: $2.4 trillion, Ukraine GDP decline: 29.3%

### The Fix

```python
# ✅ CORRECT - Includes query parameter
class ExtractDocumentNumbers(dspy.Signature):
    """Extract query-relevant numerical data points from document text.

    Focus on numbers that directly address the research query.
    Skip generic index data unless it relates to the query topic.

    For war economic impact queries, prioritize:
    - GDP changes (pre-war vs post-war)
    - Sanctions costs and economic penalties
    - Reconstruction spending
    - Casualty counts and refugee numbers
    - Trade volume changes

    Skip generic commodity prices unless they show war-related changes.
    """
    query = dspy.InputField(desc="Research query for context")
    document_text = dspy.InputField(desc="Document content to extract numbers from")
    document_title = dspy.InputField(desc="Document title for context")
    structured_numbers = dspy.OutputField(
        desc="JSON array of query-relevant numbers with label, numeric value, unit, context, and year"
    )
```

**Rule**: DSPy modules need full context for good decisions. Always include query parameter.

---

## 3. Missing Query Context

**Anti-Pattern**: Signatures only process document content
**Impact**: High - Can't prioritize by relevance
**Source**: Multiple analyst and researcher tools (before fix)

### The Problem

```python
# ❌ WRONG - No query context
class ExtractData(dspy.Signature):
    document_text = dspy.InputField(desc="Document content")
    extracted_data = dspy.OutputField(desc="Extracted data")
```

**Impact**:
- Number extraction doesn't know which numbers are relevant
- Citation building can't prioritize by query relevance
- Content filtering loses semantic signal

### The Fix

```python
# ✅ CORRECT - Always pass query context
class ExtractData(dspy.Signature):
    query = dspy.InputField(desc="User's research question")
    document_text = dspy.InputField(desc="Document content")
    document_title = dspy.InputField(desc="Document title for context")
    extracted_data = dspy.OutputField(desc="Query-relevant extracted data")
```

**Rule**: Query context is required for relevance.

---

## 4. Data Models in Wrong Layer

**Anti-Pattern**: Pydantic models in presentation layer
**Impact**: High - Tight coupling, testability issues
**Source**: `api/models.py` (80 lines) - before fix

### The Problem

```python
# ❌ WRONG - Data model in presentation layer
# api/models.py
class UIDescriptor(BaseModel):
    id: str
    type: str
    content: dict
```

**Issues**:
- Tight coupling between API and business logic
- Difficult to test business logic in isolation
- Violates Dependency Inversion Principle
- Import confusion (which `UIDescriptor` is the real one?)

### The Fix

```python
# ✅ CORRECT - Domain entity in domain layer
# domain/entities/ui_descriptor.py (canonical)
class UIDescriptor(BaseModel):
    """Canonical UI descriptor entity."""
    id: str
    type: str
    content: dict

# api/models.py (deprecated alias)
from domain.entities.ui_descriptor import UIDescriptor as UIDescriptorEntity
UIDescriptor = UIDescriptorEntity  # Backward compatibility
```

**Rule**: Domain entities → `domain/entities/`, NOT `api/`

---

## 5. God Objects

**Anti-Pattern**: Single file with 4+ responsibilities
**Impact**: High - Unmaintainable, hard to test
**Source**: `api/routes.py` (561 lines) - before fix

### The Problem

```python
# ❌ WRONG - 561-line file with 4+ responsibilities
# api/routes.py
@router.get("/health")  # Responsibility 1
async def health_check(): ...

@router.post("/generate-widget")  # Responsibility 2
async def generate_widget(): ...

@router.post("/search")  # Responsibility 3
async def search_endpoint(): ...

@router.websocket("/ws/search")  # Responsibility 4
async def search_websocket(): ...

@router.websocket("/ws/generate-widget")  # Responsibility 5
async def generate_widget_master_agent(): ...
```

**Issues**:
- Unmaintainable (561 lines in one file)
- Hard to test (all routes coupled)
- Merge conflicts inevitable
- Violates Single Responsibility Principle

### The Fix

```python
# ✅ CORRECT - Split into focused files
# api/routes/health.py (23 lines)
# api/routes/search.py (129 lines)
# api/routes/master_agent.py (153 lines)
# api/routes/__init__.py (33 lines) - composition
```

**Rule**: Split files when >3 distinct responsibilities or >150 lines.

---

## 6. Architectural Boundary Violations

**Anti-Pattern**: API layer imports directly from service layer
**Impact**: High - Tight coupling
**Source**: `api/routes.py` (18 direct imports) - before fix

### The Problem

```python
# ❌ WRONG - Direct import from services
from services.multihop_search.agents import MultiHopSearchAgent
from services.pipeline.analyst import AnalystAgent
from services.pipeline.researcher import ResearcherAgent
# ... 15 more direct imports
```

**Issues**:
- Tight coupling between presentation and business logic
- Cannot change business logic without breaking API
- Violates Dependency Inversion Principle
- Makes testing difficult

### The Fix

```python
# ✅ CORRECT - Use application layer
# Created application/use_cases/search.py
class SearchUseCase:
    def __init__(self, search_service: SearchService):
        self._search_service = search_service

# api/routes/search.py
from application.use_cases.search import get_search_use_case
use_case = get_search_use_case()  # Dependency injection
answer = await use_case.search(request)
```

**Rule**: API → application layer → services. Never import services/ from api/.

---

## 7. File Size Violations

**Anti-Pattern**: Files exceed 150-line guideline
**Impact**: Medium - Maintainability
**Source**: Multiple service files (before Phase 5 refactoring)

### The Problem

| File | Lines | Issue |
|------|-------|-------|
| `services/multihop_search/agents.py` | 399 | Multiple agents in one file |
| `services/master_agent/master_agent.py` | 334 | Orchestration + pipeline logic |
| `services/tools/analyst_tools.py` | 263 | Multiple tools + type utils |

### The Fix

**Extract when files grow >150 lines**:
```python
# Extract related functionality
# Group by responsibility
# Create shared modules for common utilities
```

**Rule**: Max 150 lines per file. Extract early, don't wait.

---

## 8. Data Model Scattering

**Anti-Pattern**: Same schema in 3 locations
**Impact**: Medium - Import confusion, sync risk
**Source**: `UIDescriptor` in 3 places (before Phase 6)

### The Problem

```
UIDescriptor found in 3 places:
├── models/schemas.py (deprecated alias)
├── services/widget_spawner/models.py (deprecated alias)
└── domain/entities/ui_descriptor.py (canonical location)
```

**Issues**:
- Import confusion (which one is correct?)
- Synchronization risk (changes might not propagate)
- Violates DRY principle
- Maintenance burden

### The Fix

```python
# ONE canonical source:
# domain/entities/ui_descriptor.py
class UIDescriptor(BaseModel):
    """Canonical UI descriptor entity."""
    # ... fields

# All other locations import from canonical:
# models/schemas.py
from domain.entities.ui_descriptor import UIDescriptor as UIDescriptorEntity
UIDescriptor = UIDescriptorEntity  # Backward compatibility alias
```

**Rule**: Single source of truth. One canonical location per entity.

---

## 9. Code Duplication (DRY Violations)

**Anti-Pattern**: Same helper functions in multiple files
**Impact**: Low - Maintenance burden
**Source**: Type conversion helpers duplicated

### The Problem

```python
# ❌ WRONG - Same function in 2 files
# services/tools/analyst_tools.py
def _to_float(value: Any, default: float = 0.0) -> float:
    # ... implementation

# services/tools/contextualizer_tools.py
def _to_float(value: Any, default: float = 0.0) -> float:
    # ... same implementation
```

**Issues**:
- Maintenance burden (bug fix needs to be replicated)
- Inconsistency risk (implementations might drift)
- Violates DRY principle

### The Fix

```python
# ✅ CORRECT - Single shared module
# services/tools/common/type_utils.py
def _to_float(value: Any, default: float = 0.0) -> float:
    # ... implementation

# All files import from shared
from services.tools.common.type_utils import _to_float, _to_bool
```

**Rule**: Extract duplicated code to `common/` or `shared/` modules.

---

## 10. Relative Imports

**Anti-Pattern**: `from .module import function`
**Impact**: Medium - Import confusion
**Source**: CLAUDE_POLICY.md violation

### The Problem

```python
# ❌ WRONG - Relative import
from .module import function
from ..service import Service
```

**Issues**:
- Confusing (where is the file?)
- Breaks when files move
- Hard to search for imports

### The Fix

```python
# ✅ CORRECT - Absolute import
from application.use_cases.search import SearchUseCase
from services.pipeline.analyst import AnalystAgent
```

**Rule**: ALWAYS use absolute imports. No `from .` or `from ..`.

---

## 11. Assuming Numeric Returns

**Anti-Pattern**: Expect LLM to return numbers/bools
**Impact**: High - Type errors everywhere
**Source**: All DSPy modules (before adding type conversion)

### The Problem

```python
# ❌ WRONG - Assumes numeric return
result = assess_data(query=query)
if result.data_completeness > 0.7:  # TypeError: '>' not supported between str and float
    pass
```

**Reality**: LLMs return "High", "0.75", "yes", etc. - not numbers/bools.

### The Fix

```python
# ✅ CORRECT - Always convert
from services.tools.common.type_utils import _to_float, _to_bool

result = assess_data(query=query)
completeness = _to_float(result.data_completeness, default=0.5)
needs_research = _to_bool(result.needs_more_research, default=False)

if completeness > 0.7:
    pass
```

**Rule**: LLMs return text, not numbers/bools. Always convert with fallbacks.

---

## 12. CodeAct for Small LLMs

**Anti-Pattern**: Using CodeAct with qwen3:8b
**Impact**: High - Tool calling fails
**Source**: `services/tools/calendar/calendar_agent.py` (before fix)

### The Problem

```python
# ❌ WRONG - CodeAct fails on small LLMs
self.codeact = dspy.CodeAct(
    signature=CalendarQuery,
    tools=[get_current_date, calculate_date_offset],
    max_iters=3,
)
```

**Result**: qwen3:8b returns conversational markdown instead of JSON → parse errors.

### The Fix

```python
# ✅ CORRECT - Use ReAct for small LLMs
self.react = dspy.ReAct(
    signature=CalendarQuery,
    tools=[get_current_date, calculate_date_offset],
    max_iters=3,
)
```

**Rule**: For models <10B params, ALWAYS use ReAct for tool-based agents.

---

## 13. Not Chunking Large Inputs

**Anti-Pattern**: Send entire document to LLM
**Impact**: High - Context overflow, corrupted outputs
**Source**: `InsightExtractorModule` (before fix)

### The Problem

```python
# ❌ WRONG - No chunking
class InsightExtractorModule(dspy.Module):
    def forward(self, document_text: str) -> dspy.Prediction:
        # Send entire document (may be 1600+ chars)
        result = self.extract(document_text=document_text)
        return result
```

**Result**: Inputs >500 chars cause truncated/corrupted outputs.

### The Fix

```python
# ✅ CORRECT - Chunking + iteration
MAX_CHUNK_SIZE = 500
OVERLAP = 100
ITERATIONS = 3

class InsightExtractorModule(dspy.Module):
    def forward(self, document_text: str) -> dspy.Prediction:
        if len(document_text) <= MAX_CHUNK_SIZE:
            return self._extract_single(document_text)
        return self._extract_iterative(document_text)
```

**Rule**: Always chunk inputs >500 chars for qwen3:8b.

---

## 14. Generic Predict Signatures

**Anti-Pattern**: Using `dspy.Predict("data -> structured_data")`
**Impact**: High - Returns unparsable string
**Source**: `DataStructurerModule` (before fix)

### The Problem

```python
# ❌ WRONG - Generic signature
self.structure = dspy.Predict("beautiful_data -> organized_data")
result = self.structure(beautiful_data=raw_data)
# result.organized_data is a STRING blob
```

### The Fix

```python
# ✅ CORRECT - Explicit signature
class StructureDataChunk(dspy.Signature):
    """Structure raw data into key facts, trends, and comparisons."""
    data_chunk = dspy.InputField(desc="Data to structure (max 500 chars)")
    key_facts = dspy.OutputField(desc="Key facts from data, numbered 1-5")
    trends = dspy.OutputField(desc="Trends from data, numbered 1-3")
    comparisons = dspy.OutputField(desc="Comparisons from data, numbered 1-2")

self.structure = dspy.ChainOfThought(StructureDataChunk)
```

**Rule**: NEVER use generic Predict. Always use explicit signatures with named output fields.

---

## 15. Hard-Coded Semantic Rules

**Anti-Pattern**: Keyword matching for classification
**Impact**: Medium - Brittle, doesn't generalize
**Source**: `WidgetMatcherModule` (before fix)

### The Problem

```python
# ❌ WRONG - Hard-coded rules
SEMANTIC_RULES = {
    "stock": "chart",
    "price": "chart",
    "weather": "card",
}

def match_widget(query: str) -> str:
    for keyword, widget in SEMANTIC_RULES.items():
        if keyword in query.lower():
            return widget
    return "markdown"
```

**Issues**:
- "equity values" → "markdown" (should be "chart")
- Brittle keyword matching
- Doesn't generalize

### The Fix

```python
# ✅ CORRECT - Few-shot learning
class SelectWidgetSignature(dspy.Signature):
    """Select widgets based on query intent and data characteristics.

    SEMANTIC PATTERNS (learn from these examples):

    Example 1:
    Query: "Show real-time stock prices"
    Data: numerical_time_series
    Selected: chart
    Reasoning: Stock prices are time-series data...

    NOTE: These are EXAMPLES to learn from, not hard-coded rules.
    """
    query = dspy.InputField(desc="User's natural language query")
    data_type = dspy.InputField(desc="Type of data available")
    selected_widgets = dspy.OutputField(desc="JSON array of widget names")
```

**Rule**: Use few-shot examples in signature for classification tasks.

---

## 16. Forgetting DSPy Sync Warmup

**Anti-Pattern**: Direct streaming without warmup
**Impact**: High - Silent failures
**Source**: `services/pipeline/analyst.py` (before fix)

### The Problem

```python
# ❌ WRONG - No warmup
stream = dspy.streamify(module, ...)
for chunk in stream(input=data):
    print(chunk)  # Empty output!
```

### The Fix

```python
# ✅ CORRECT - Sync warmup first
_ = module(query="warmup")  # Synchronous call
stream = dspy.streamify(module, ...)
for chunk in stream(input=data):
    print(chunk)  # Works!
```

**Rule**: ALWAYS do synchronous call before DSPy streaming.

---

## 17: WebSocket Callbacks Without State Check

**Anti-Pattern**: Callbacks continue after error
**Impact**: Medium - Cascading WebSocket exceptions
**Source**: `api/routes/master_agent.py` (before fix)

### The Problem

```python
# ❌ WRONG - No state check
async def send_progress(checkpoint: str):
    await websocket.send_json({"type": "progress", "checkpoint": checkpoint})

await run_pipeline(send_progress)  # Callbacks continue after error
```

### The Fix

```python
# ✅ CORRECT - Connection state tracking
connection_active = True

async def send_progress(checkpoint: str):
    if not connection_active:  # Check flag
        return
    try:
        await websocket.send_json({"type": "progress", "checkpoint": checkpoint})
    except Exception:
        pass
```

**Rule**: ALWAYS track connection state for WebSocket callbacks.

---

## 18. No Progressive Feedback

**Anti-Pattern**: Silent processing, only final result
**Impact**: Low - Poor UX
**Source**: Initial implementation

### The Problem

```python
# ❌ WRONG - No feedback
@router.websocket("/ws/generate-widget")
async def generate_widget(websocket: WebSocket):
    await websocket.accept()
    result = await run_pipeline()  # Takes 30 seconds, no feedback
    await websocket.send_json(result)
```

**User sees**: Loading spinner for 30 seconds, no indication of progress.

### The Fix

```python
# ✅ CORRECT - Progressive feedback
async def run_pipeline_with_feedback(send_progress):
    for phase in ["analyst", "researcher", "designer"]:
        await send_progress(phase, "running", {})
        result = await execute_phase(phase)
        await send_progress(phase, "passed", {"output": result})
```

**Rule**: Send events after each phase for long-running operations.

---

## 19. Brittle Serialization

**Anti-Pattern**: Assume Pydantic model
**Impact**: Medium - Crashes on unknown types
**Source**: `api/routes/master_agent.py` (before fix)

### The Problem

```python
# ❌ WRONG - Assumes Pydantic
await websocket.send_json(delivery_plan.model_dump())  # Crashes if no model_dump()
```

### The Fix

```python
# ✅ CORRECT - Three-tier fallback
def _serialize_safely(obj: Any) -> dict:
    try:
        return obj.model_dump()
    except Exception:
        pass
    try:
        return {f: getattr(obj, f) for f in obj.__dataclass_fields__}
    except Exception:
        pass
    return {"error": "Serialization failed"}

await websocket.send_json(_serialize_safely(delivery_plan))
```

**Rule**: Never crash on serialization. Use fallbacks.

---

## 20. No Mock Mode

**Anti-Pattern**: Can't test without LLM
**Impact**: Low - Slower development
**Source**: Initial implementation

### The Problem

```python
# ❌ WRONG - Always calls LLM
@router.websocket("/ws/generate-widget")
async def generate_widget(websocket: WebSocket):
    await websocket.accept()
    result = await llm_pipeline(query)  # Can't test UI without LLM
```

### The Fix

```python
# ✅ CORRECT - Mock mode support
@router.websocket("/ws/generate-widget")
async def generate_widget(websocket: WebSocket):
    await websocket.accept()

    if settings.mock_mode:
        await handle_mock_mode(websocket, session_id, user_query)
        return

    result = await llm_pipeline(query)
```

**Rule**: Include mock mode from day 1 for fast frontend development.

---

## 21. Magic Numbers

**Anti-Pattern**: Hard-coded values
**Impact**: Low - Maintainability
**Source**: Various files

### The Problem

```python
# ❌ WRONG - Magic numbers
if len(text) > 500:  # What is 500?
    chunk_size = 100  # What is 100?
    iterations = 3  # Why 3?
```

### The Fix

```python
# ✅ CORRECT - Named constants
MAX_CHUNK_SIZE = 500  # qwen3:8b context limit / 8
OVERLAP = 100  # Typical paragraph length
ITERATIONS = 3  # Covers 1500 chars

if len(text) > MAX_CHUNK_SIZE:
    for i in range(ITERATIONS):
        chunk_size = MAX_CHUNK_SIZE - OVERLAP
```

**Rule**: Use named constants for all magic numbers.

---

## 22. Silent Failures Without Logging

**Anti-Pattern**: Exception swallowed without log
**Impact**: Low - Debugging difficulty
**Source**: WebSocket error handlers

### The Problem

```python
# ❌ WRONG - Silent failure
try:
    await websocket.send_json(data)
except Exception:
    pass  # What went wrong?
```

### The Fix

```python
# ✅ CORRECT - Log before silent failure
import logging

logger = logging.getLogger(__name__)

try:
    await websocket.send_json(data)
except Exception as e:
    logger.debug(f"WebSocket send failed: {e}")  # Log at debug level
    pass  # Still don't crash
```

**Rule**: Log errors before silent exception handling.

---

## Summary Table: What to Avoid

| # | Anti-Pattern | Impact | Fix |
|---|--------------|--------|-----|
| 1 | Verbose field descriptions | Medium | Instructions in docstring |
| 2 | Generic signatures (no query) | High | Add query parameter |
| 3 | Missing query context | High | Always pass query |
| 4 | Data models in api/ | High | Use domain/entities/ |
| 5 | God objects | High | Split >150 lines |
| 6 | Architectural violations | High | Use application layer |
| 7 | File size violations | Medium | Extract early |
| 8 | Data model scattering | Medium | Single source of truth |
| 9 | Code duplication | Low | Extract to common/ |
| 10 | Relative imports | Medium | Use absolute imports |
| 11 | Assuming numeric returns | High | Always convert with fallbacks |
| 12 | CodeAct for small LLMs | High | Use ReAct |
| 13 | Not chunking large inputs | High | Chunk >500 chars |
| 14 | Generic Predict | High | Use explicit signatures |
| 15 | Hard-coded rules | Medium | Use few-shot learning |
| 16 | Forgetting sync warmup | High | Always warm up before streaming |
| 17 | No connection state | Medium | Use boolean flag |
| 18 | No progressive feedback | Low | Send events after each phase |
| 19 | Brittle serialization | Medium | Use three-tier fallback |
| 20 | No mock mode | Low | Include from day 1 |
| 21 | Magic numbers | Low | Use named constants |
| 22 | Silent failures | Low | Log before pass |

---

## Critical Rules for Real AgentX

1. ❌ **Never use verbose field descriptions** - Keep to 5-10 words
2. ❌ **Never forget query context** - Always include query parameter
3. ❌ **Never put data models in api/** - Use domain/entities/
4. ❌ **Never create god objects** - Split files >150 lines
5. ❌ **Never import services/ from api/** - Use application layer
6. ❌ **Never assume numeric returns** - LLMs return text
7. ❌ **Never use CodeAct for small LLMs** - Use ReAct
8. ❌ **Never send entire document to LLM** - Chunk >500 chars
9. ❌ **Never use generic Predict** - Use explicit signatures
10. ❌ **Never hard-code semantic rules** - Use few-shot learning

---

## Conclusion

R014 made all these mistakes initially and spent 2-3 weeks fixing them. Start Real AgentX with the correct patterns from day 1.

# What to Replicate in Real AgentX

## Summary
**Total Items to Replicate**: 27
**Categories**: Architecture, DSPy Patterns, Technical Solutions, Behaviors
**Priority**: All REQUIRED or HIGH priority

---

## 1. Clean Architecture from Day 1

**Priority**: ✅ REQUIRED
**Source**: R014 refactoring Phases 1-4
**Reason**: R014 took 2-3 weeks to refactor from monolithic to Clean Architecture. Start with the correct structure.

**Action**: Create directory structure before writing any code:
```
real_agentx/
├── core/ - Config, DI, middleware
├── domain/ - Entities, repositories, services
├── application/ - Use cases, DTOs, mappers
├── infrastructure/ - DB, HTTP, external APIs
└── presentation/ - FastAPI routes, GraphQL
```

**Files to Copy**:
- `application/use_cases/search.py` - Use case pattern
- `domain/entities/ui_descriptor.py` - Entity pattern
- `application/dtos/requests/*.py` - DTO pattern

---

## 2. Application Layer Pattern

**Priority**: ✅ REQUIRED
**Source**: R014 `application/use_cases/`
**Reason**: API depends on abstractions, not concrete services. Enables testing and flexibility.

**Action**: All API endpoints go through use cases:
```python
# application/use_cases/{feature}.py
class {Feature}UseCase:
    def __init__(self, service: {Service}):
        self._service = service

    def execute(self, request: {Request}DTO) -> {Response}DTO:
        result = self._service.do_something(request.param)
        return {Response}DTO(field=result)

# Dependency injection
_use_case: {Feature}UseCase | None = None

def get_{feature}_use_case() -> {Feature}UseCase:
    global _use_case
    if _use_case is None:
        service = {Service}()
        _use_case = {Feature}UseCase(service)
    return _use_case

# API endpoint
@router.post("/{feature}")
async def {feature}_endpoint(param: str):
    use_case = get_{feature}_use_case()
    dto_request = {Request}DTO(param=param)
    dto_response = await use_case.execute(dto_request)
    return dto_response.model_dump()
```

**Files to Copy**:
- `application/use_cases/search.py`
- `application/use_cases/master_agent.py`
- `application/dtos/requests/search.py`
- `application/dtos/responses/search.py`

---

## 3. Type Conversion Helpers

**Priority**: ✅ REQUIRED
**Source**: `services/tools/common/type_utils.py` (91 lines)
**Reason**: LLMs return text, not numbers/bools. Without conversion, type errors occur everywhere.

**Action**: Include type_utils from day 1:
```python
# core/llm/type_utils.py
from typing import Any

def _to_float(value: Any, default: float = 0.0) -> float:
    """Convert value to float with default fallback."""
    # ... (see battle_tested_solutions.md for full implementation)

def _to_bool(value: Any, default: bool = False) -> bool:
    """Convert value to bool with default fallback."""
    # ... (see battle_tested_solutions.md for full implementation)

def _to_int(value: Any, default: int = 0) -> int:
    """Convert value to int with default fallback."""
    # ... (see battle_tested_solutions.md for full implementation)

# Usage in all DSPy modules
from core.llm.type_utils import _to_float, _to_bool, _to_int

result = module(input=data)
score = _to_float(result.score, default=0.5)
flag = _to_bool(result.flag, default=False)
count = _to_int(result.count, default=0)
```

**File to Copy**:
- `services/tools/common/type_utils.py`

---

## 4. Async/Sync Compatibility Layer

**Priority**: ✅ REQUIRED
**Source**: `services/tools/researcher/search_async_wrapper.py`
**Reason**: Calling async functions from sync contexts (DSPy modules) causes event loop errors.

**Action**: Include async_compat layer from day 1:
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

# In sync context (DSPy module)
data = run_async(fetch_data())
```

**File to Copy**:
- `services/tools/researcher/search_async_wrapper.py`

---

## 5. Chunking + Iteration for Large Inputs

**Priority**: ✅ REQUIRED
**Source**: `services/tools/analyst/insight_extractor.py`
**Reason**: qwen3:8b context window (~4K tokens) exceeded by inputs >500 chars, causing corrupted outputs.

**Action**: Use chunking for any variable-length input:
```python
MAX_CHUNK_SIZE = 500  # For qwen3:8b
OVERLAP = 100
ITERATIONS = 3

class ChunkedProcessor(dspy.Module):
    def forward(self, text: str) -> dspy.Prediction:
        if len(text) <= MAX_CHUNK_SIZE:
            return self._process_single(text)
        return self._process_chunked(text)

    def _process_chunked(self, text: str) -> dspy.Prediction:
        results = []
        for i in range(ITERATIONS):
            start = i * (MAX_CHUNK_SIZE - OVERLAP)
            end = start + MAX_CHUNK_SIZE
            chunk = text[start:end]
            result = self.process_chunk(chunk=chunk)
            results.append(result)
        return self._combine_results(results)
```

**Parameters for Different Models**:
| Model | Context | MAX_CHUNK_SIZE | OVERLAP | ITERATIONS |
|-------|---------|----------------|---------|------------|
| qwen3:8b | ~4K | 500 | 100 | 3 |
| gemma3:4b | ~8K | 1000 | 200 | 2-3 |
| GPT-4 | ~32K | 4000 | 500 | 1-2 |

---

## 6. ReAct Instead of CodeAct

**Priority**: ✅ CRITICAL (for small LLMs)
**Source**: `services/tools/calendar/calendar_agent.py`
**Reason**: CodeAct fails on qwen3:8b and gemma3:4b (returns conversational markdown, not JSON).

**Action**: Always use ReAct for small LLMs:
```python
# ❌ WRONG for small LLMs
agent = dspy.CodeAct(
    signature=MySignature,
    tools=[tool1, tool2],
    max_iters=3,
)

# ✅ CORRECT for small LLMs
agent = dspy.ReAct(
    signature=MySignature,
    tools=[tool1, tool2],
    max_iters=3,
)
```

**When to Use**:
- **ReAct**: Models <10B params (qwen3:8b, gemma3:4b)
- **CodeAct**: Models >10B params (GPT-4, Claude 3)

---

## 7. Explicit Signatures with Named Fields

**Priority**: ✅ REQUIRED
**Source**: `services/tools/researcher/data_structurer.py`
**Reason**: Generic `Predict` returns unparsable string. Explicit signatures return structured fields.

**Action**: Never use generic signatures:
```python
# ❌ WRONG - returns string
module = dspy.Predict("data -> structured_data")
result = module(data=raw_text)
# result.structured_data is a STRING blob

# ✅ CORRECT - returns structured fields
class StructureData(dspy.Signature):
    """Structure data into fields."""
    data = dspy.InputField(desc="Input data")
    field1 = dspy.OutputField(desc="Field 1")
    field2 = dspy.OutputField(desc="Field 2")

module = dspy.ChainOfThought(StructureData)
result = module(data=raw_text)
# result.field1, result.field2 are separate fields
```

---

## 8. Few-Shot Semantic Learning

**Priority**: ✅ HIGH
**Source**: `services/tools/selectors/widget_matcher.py`
**Reason**: Hard-coded rules don't generalize. Few-shot examples enable semantic understanding.

**Action**: Include examples in signatures for classification tasks:
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

## 9. Connection State Tracking

**Priority**: ✅ REQUIRED
**Source**: `api/routes/master_agent.py`
**Reason**: Prevents cascading "WebSocket closed" exceptions after error/disconnect.

**Action**: Always use connection state flag:
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

## 10. Progressive Feedback Events

**Priority**: ✅ REQUIRED
**Source**: `api/routes/master_agent.py`
**Reason**: Better UX - user sees progress through pipeline, not just loading spinner.

**Action**: Send events after each phase:
```python
async def run_long_operation(
    progress_callback: Callable[[str, str, dict], Awaitable[None]],
) -> Result:
    steps = ["step1", "step2", "step3"]

    for step in steps:
        await progress_callback(step, "running", {})

        result = await execute_step(step)

        await progress_callback(step, "passed", {"output": result})

    return final_result
```

---

## 11. Three-Tier Serialization Fallback

**Priority**: ✅ HIGH
**Source**: `api/routes/master_agent.py`
**Reason**: Never crashes on unknown data types.

**Action**: Always use safe serialization:
```python
def _serialize_safely(obj: Any) -> dict:
    """Three-tier serialization fallback."""

    # Tier 1: Pydantic
    try:
        return obj.model_dump()
    except Exception:
        pass

    # Tier 2: Manual
    try:
        return {field: getattr(obj, field) for field in obj.__dataclass_fields__}
    except Exception:
        pass

    # Tier 3: Minimal
    return {"error": "Serialization failed", "type": str(type(obj))}
```

---

## 12. Mock Mode Support

**Priority**: ✅ HIGH
**Source**: `api/mock_handler.py`
**Reason**: Fast development without LLM dependency. Test frontend while backend is in progress.

**Action**: Include mock mode from day 1:
```python
# config/settings.py
class Settings(BaseSettings):
    mock_mode: bool = False

# API endpoint
@router.websocket("/ws/{endpoint}")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    if settings.mock_mode:
        await handle_mock_mode(websocket, session_id, user_query)
        return

    # ... real implementation
```

---

## 13. DSPy Sync Warmup for Streaming

**Priority**: ✅ REQUIRED
**Source**: `services/pipeline/analyst.py`
**Reason**: DSPy streaming requires synchronous initialization before async streaming.

**Action**: Always warm up before streaming:
```python
def create_streaming_module(module: dspy.Module) -> dspy.Module:
    """Create streaming wrapper with sync warmup."""

    # Step 1: Synchronous warmup
    _ = module(query="warmup")

    # Step 2: Create streaming wrapper
    stream = dspy.streamify(
        module,
        stream_listeners=[
            StreamListener(signature_field_name="output_field", allow_reuse=True)
        ]
    )

    return stream

# Usage
module = MyDSPyModule()
streaming_module = create_streaming_module(module)
for chunk in streaming_module(input=data):
    print(chunk, end="")
```

---

## 14. Search Term Extraction Pattern

**Priority**: ✅ HIGH
**Source**: `services/tools/analyst/search_terms.py`
**Reason**: Converts conversational queries to search-engine-friendly phrases.

**Action**: Include search term extraction:
```python
class ExtractSearchTerms(dspy.Signature):
    """Extract 2-4 word search phrases from natural language query.

    Examples:
    - "Explain climate change" → ['global warming impact', 'climate change effects']
    - "Python vs JavaScript" → ['python vs javascript web development']

    Return 2-4 search terms as JSON array.
    """
    query = dspy.InputField(desc="Natural language query")
    search_terms = dspy.OutputField(desc="List of 2-4 word search phrases")

# Use ChainOfThought with n=3
extractor = dspy.ChainOfThought(ExtractSearchTerms, n=3)
```

---

## 15. Context Analysis Pattern

**Priority**: ✅ HIGH
**Source**: `services/tools/analyst/query_analyzer.py`
**Reason**: Domain classification and query type detection for routing.

**Action**: Include context analyzer:
```python
class AnalyzeQueryContext(dspy.Signature):
    """Analyze query to determine domain, query type, and urgency."""
    query = dspy.InputField(desc="User's natural language query")
    domain = dspy.OutputField(desc="Domain or field of study")
    query_type = dspy.OutputField(desc="Type of query (definition, comparison, etc.)")
    urgency = dspy.OutputField(desc="Urgency level (low, medium, high)")

# Use 3 parallel Predict calls for efficiency
domain_analyzer = dspy.Predict(AnalyzeQueryContext)
type_analyzer = dspy.Predict(AnalyzeQueryContext)
urgency_analyzer = dspy.Predict(AnalyzeQueryContext)
```

---

## 16. Single Source of Truth for Data Models

**Priority**: ✅ REQUIRED
**Source**: `domain/entities/ui_descriptor.py`
**Reason**: Prevents duplication, import confusion, synchronization issues.

**Action**: One canonical location per entity:
```python
# domain/entities/{entity}.py (CANONICAL)
class {Entity}(BaseModel):
    """Canonical {entity} entity."""
    id: str
    field1: str
    # ... all fields

# Old location (DEPRECATED)
# models/schemas.py
from domain.entities.{entity} import {Entity} as {Entity}Entity

# ⚠️ DEPRECATED: Use domain.entities.{entity}.{Entity} instead
{Entity} = {Entity}Entity  # type: ignore
```

---

## 17. File Size Limits

**Priority**: ✅ REQUIRED
**Source**: R014 refactoring Phase 5
**Reason**: Files >150 lines become unmaintainable god objects.

**Action**: Extract when files grow >150 lines:
```python
# Identify distinct responsibilities
class BigClass:
    def responsibility_a(self): ...
    def responsibility_b(self): ...
    def responsibility_c(self): ...

# Extract to separate files
# big_class.py (main logic)
class BigClass:
    def __init__(self):
        self.helper_a = ResponsibilityA()
        self.helper_b = ResponsibilityB()

# responsibility_a.py
class ResponsibilityA:
    def execute(self): ...

# responsibility_b.py
class ResponsibilityB:
    def execute(self): ...
```

---

## 18. Absolute Imports Only

**Priority**: ✅ REQUIRED
**Source**: CLAUDE_POLICY.md
**Reason**: Relative imports cause confusion and maintenance issues.

**Action**: Always use absolute imports:
```python
# ❌ WRONG
from .module import function
from ..service import Service

# ✅ CORRECT
from application.use_cases.search import SearchUseCase
from services.pipeline.analyst import AnalystAgent
from domain.entities.ui_descriptor import UIDescriptor
```

---

## 19. Ruff Compliance

**Priority**: ✅ REQUIRED
**Source**: CLAUDE_POLICY.md
**Reason**: Consistent code quality, automatic formatting.

**Action**: Run before every commit:
```bash
ruff check . --fix
ruff format .
```

---

## 20. Pyrefly Type Checking

**Priority**: ✅ REQUIRED
**Source**: CLAUDE_POLICY.md
**Reason**: Catch type errors before runtime.

**Action**: Run frequently:
```bash
pyrefly check . --summarize-errors
```

**Special Patterns**:
```python
# PyTorch device
self._torch_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # type: ignore[read-only]

# torch.hub.load indexing
result = torch.hub.load(...)
self.model = result[0]  # type: ignore[index]

# MCP imports
from mcp__tavily__tavily_search import tavily_search  # type: ignore[import]
```

---

## 21. Regex-Based Numeric Extraction

**Priority**: ✅ HIGH
**Source**: `services/tools/researcher/citation_builder.py`
**Reason**: LLM returns scores in conversational format.

**Action**: Use regex extraction:
```python
import re
from typing import Any

def extract_number(text: Any, default: float = 0.0) -> float:
    """Extract first number from text with fallbacks."""

    if isinstance(text, (int, float)):
        return float(text)

    if isinstance(text, str):
        try:
            return float(text)
        except ValueError:
            pass

        match = re.search(r'(\d+\.?\d*)', text)
        if match:
            value = float(match.group(1))
            if value > 1.0 and '%' in text:
                return value / 100.0
            return value

    return default
```

---

## 22. Session Tracking with Truncated UUID

**Priority**: ✅ HIGH
**Source**: `api/routes/master_agent.py`
**Reason**: Readable logs, session tracing.

**Action**:
```python
import uuid

session_id = uuid.uuid4().hex
session_short = session_id[:8]
print(f"[{session_short}] Log message")
```

---

## 23. Device Context Normalization

**Priority**: ✅ HIGH
**Source**: `api/routes/master_agent.py`
**Reason**: Frontend may send string or object.

**Action**:
```python
def normalize_device_context(device_context: Any) -> str:
    """Normalize device context to string."""
    if isinstance(device_context, str):
        return device_context
    if isinstance(device_context, dict):
        return device_context.get("type", "desktop")
    return "desktop"  # Default
```

---

## 24. ChainOfThought for Complex Tasks

**Priority**: ✅ HIGH
**Source**: Multiple modules
**Reason**: Better reasoning before output.

**Action**: Use ChainOfThought for complex tasks:
```python
# Simple task
module = dspy.Predict(SimpleSignature)

# Complex task (requires reasoning)
module = dspy.ChainOfThought(ComplexSignature)
```

---

## 25. Dependency Injection Pattern

**Priority**: ✅ HIGH
**Source**: `core/dependencies.py`
**Reason**: Global singletons with getter functions.

**Action**:
```python
# core/dependencies.py
_use_case: SearchUseCase | None = None

def get_search_use_case() -> SearchUseCase:
    global _use_case
    if _use_case is None:
        service = SearchService()
        _use_case = SearchUseCase(service)
    return _use_case

# Usage
from core.dependencies import get_search_use_case

use_case = get_search_use_case()
```

---

## 26. Pydantic Settings Pattern

**Priority**: ✅ HIGH
**Source**: `core/config/settings.py`
**Reason**: Type-safe configuration with environment variables.

**Action**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "AgentX"
    version: str = "0.1.0"
    port: int = 8000
    debug: bool = True
    mock_mode: bool = False
    llm_model: str = "gemma3:4b"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

# Usage
from core.config.settings import settings

if settings.mock_mode:
    ...
```

---

## 27. WebSocket Event Types

**Priority**: ✅ REQUIRED
**Source**: `api/routes/master_agent.py`
**Reason**: Consistent event structure for frontend integration.

**Action**: Use standard event types:
```python
# Progress events
{"type": "qa_progress", "data": {"checkpoint": "phase", "status": "running", "details": {}}}

# Widget events
{"type": "widget", "data": {...widget_descriptor...}}

# Complete events
{"type": "complete", "data": {...delivery_plan...}}

# Error events
{"type": "error", "message": "Error message"}
```

---

## Summary Table: What to Replicate

| # | Item | Priority | Category | File to Copy |
|---|------|----------|----------|--------------|
| 1 | Clean Architecture | REQUIRED | Architecture | Create structure |
| 2 | Application Layer | REQUIRED | Architecture | application/use_cases/*.py |
| 3 | Type Conversion | REQUIRED | Technical | services/tools/common/type_utils.py |
| 4 | Async/Sync Wrapper | REQUIRED | Technical | services/tools/researcher/search_async_wrapper.py |
| 5 | Chunking + Iteration | REQUIRED | DSPy | services/tools/analyst/insight_extractor.py |
| 6 | ReAct > CodeAct | CRITICAL | DSPy | services/tools/calendar/calendar_agent.py |
| 7 | Explicit Signatures | REQUIRED | DSPy | services/tools/researcher/data_structurer.py |
| 8 | Few-Shot Learning | HIGH | DSPy | services/tools/selectors/widget_matcher.py |
| 9 | Connection State | REQUIRED | WebSocket | api/routes/master_agent.py |
| 10 | Progressive Feedback | REQUIRED | WebSocket | api/routes/master_agent.py |
| 11 | Three-Tier Serialization | HIGH | WebSocket | api/routes/master_agent.py |
| 12 | Mock Mode | HIGH | Testing | api/mock_handler.py |
| 13 | DSPy Sync Warmup | REQUIRED | Streaming | services/pipeline/analyst.py |
| 14 | Search Term Extraction | HIGH | DSPy | services/tools/analyst/search_terms.py |
| 15 | Context Analysis | HIGH | DSPy | services/tools/analyst/query_analyzer.py |
| 16 | Single Source of Truth | REQUIRED | Architecture | domain/entities/ui_descriptor.py |
| 17 | File Size Limits | REQUIRED | Code Quality | All files <150 lines |
| 18 | Absolute Imports | REQUIRED | Code Quality | All files |
| 19 | Ruff Compliance | REQUIRED | Code Quality | All files |
| 20 | Pyrefly Type Checking | REQUIRED | Code Quality | All files |
| 21 | Regex Extraction | HIGH | Technical | services/tools/researcher/citation_builder.py |
| 22 | Session Tracking | HIGH | WebSocket | api/routes/*.py |
| 23 | Device Context Flex | HIGH | WebSocket | api/routes/master_agent.py |
| 24 | ChainOfThought | HIGH | DSPy | Multiple modules |
| 25 | Dependency Injection | HIGH | Architecture | core/dependencies.py |
| 26 | Pydantic Settings | HIGH | Config | core/config/settings.py |
| 27 | WebSocket Events | REQUIRED | WebSocket | api/routes/*.py |

---

## Critical Rules for Real AgentX

1. **Start with Clean Architecture** - Don't refactor later
2. **Use application layer** - API → use cases → services
3. **Include type_utils** - From day 1
4. **Include async_compat** - From day 1
5. **Use ReAct** - For small LLMs
6. **Always chunk** - Inputs >500 chars
7. **Track connection state** - WebSocket
8. **Send progressive feedback** - Long operations
9. **Max 150 lines** - Per file
10. **Absolute imports** - No relative imports

---

## Conclusion

All 27 items are **production-tested** in R014. Start Real AgentX with these patterns from day 1 - don't repeat R014's initial mistakes.

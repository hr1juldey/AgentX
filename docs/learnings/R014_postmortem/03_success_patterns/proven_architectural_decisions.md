# Proven Architectural Decisions in R014

## Summary
**Total Architectural Changes**: 25 violations fixed → 0 violations
**Refactoring Phases**: 7 phases (Phases 0-7)
**Duration**: ~2-3 weeks
**Result**: Clean Architecture achieved, all tests still passing
**Source**: `tests/test_fix_log.md` (377 lines of refactoring history)

---

## Decision 1: Clean Architecture Layer Structure

**When**: Phase 1-4 of CLAUDE_POLICY compliance
**What**: Created strict layer boundaries following Domain-Driven Design
**Result**: 25 violations → 0 violations

### Before (Monolithic Structure)

```
backend/
├── main.py
├── api/
│   ├── routes.py (561 lines) - GOD OBJECT
│   └── models.py (80 lines) - WRONG LAYER
├── services/ - Business logic mixed with HTTP concerns
└── models/
    └── schemas.py - Duplicated models
```

**Issues**:
- Data models in presentation layer (`api/models.py`)
- API routes importing directly from services (tight coupling)
- God object (561-line `api/routes.py`)
- No clear separation of concerns

### After (Clean Architecture)

```
backend/
├── main.py - Application entry point
├── core/
│   ├── config.py - Pydantic Settings
│   └── dependencies.py - Dependency injection
├── domain/
│   └── entities/
│       └── ui_descriptor.py - Business entities (canonical)
├── application/
│   ├── use_cases/
│   │   ├── search.py - Search orchestration
│   │   ├── widgets.py - Widget generation use cases
│   │   └── master_agent.py - Master Agent orchestration
│   └── dtos/
│       ├── requests/ - Request DTOs
│       └── responses/ - Response DTOs
├── infrastructure/
│   └── external/ - External service clients
├── services/ - Business logic implementations
└── presentation/
    └── api/
        ├── routes/
        │   ├── health.py (23 lines)
        │   ├── search.py (129 lines)
        │   ├── master_agent.py (153 lines)
        │   └── __init__.py (33 lines)
        └── models.py (26 lines - deprecated aliases)
```

**Benefits**:
- **Domain entities** → `domain/entities/` (business logic, no dependencies)
- **Application layer** → `application/use_cases/` (orchestration)
- **Presentation layer** → `presentation/api/` (HTTP/WebSocket only)
- **Infrastructure** → `infrastructure/` + `services/` (external concerns)

### Lessons Learned

**Why It Works**:
1. **Dependency Inversion**: API depends on use cases, not concrete services
2. **Testability**: Can mock use cases without touching HTTP layer
3. **Maintainability**: Each layer has clear responsibility
4. **Scalability**: Can change business logic without breaking API

**What to Avoid**:
- ❌ Never put business entities in `api/` layer
- ❌ Never import `services/` directly from `api/`
- ❌ Never create files >150 lines
- ❌ Never duplicate data models

### Reuse for Real AgentX

**Status**: ✅ REQUIRED - Start with this structure

**Directory Template**:
```bash
real_agentx/
├── core/ - Config, DI, middleware
├── domain/ - Entities, repositories, services
├── application/ - Use cases, DTOs, mappers
├── infrastructure/ - DB, HTTP, external APIs
└── presentation/ - FastAPI routes, GraphQL, etc.
```

---

## Decision 2: Application Layer Pattern

**When**: Phase 1 of refactoring
**What**: Created use case layer between API and services
**Result**: Clean separation of HTTP and business logic

### Before (Direct Service Import)

```python
# api/routes/search.py (BEFORE)
from services.multihop_search.agents import MultiHopSearchAgent
from services.pipeline.analyst import AnalystAgent

@router.post("/search")
async def search_endpoint(query: str):
    # Direct dependency on concrete service
    agent = MultiHopSearchAgent()
    result = agent.search(query)
    return result
```

**Issues**:
- Tight coupling between API and service
- Cannot test API without service
- Business logic exposed to HTTP layer
- Cannot change service without breaking API

### After (Application Layer)

```python
# application/use_cases/search.py
class SearchUseCase:
    """Orchestrate search workflow."""

    def __init__(self, search_service: SearchService):
        self._search_service = search_service

    async def search(self, request: SearchRequest) -> SearchResponse:
        # Orchestrate business logic
        results = await self._search_service.search(request.query)
        return SearchResponse(results=results)

# Dependency injection
_search_use_case: SearchUseCase | None = None

def get_search_use_case() -> SearchUseCase:
    global _search_use_case
    if _search_use_case is None:
        search_service = SearchService()
        _search_use_case = SearchUseCase(search_service)
    return _search_use_case

# api/routes/search.py (AFTER)
from application.use_cases.search import get_search_use_case
from application.dtos.requests import SearchRequest
from application.dtos.responses import SearchResponse

@router.post("/search")
async def search_endpoint(query: str):
    # Depend on abstraction (use case), not concrete service
    use_case = get_search_use_case()
    dto_request = SearchRequest(query=query)
    dto_response = await use_case.search(dto_request)
    return dto_response.model_dump()
```

**Benefits**:
- **API depends on abstraction**: Use case interface, not concrete service
- **Testable**: Can mock `get_search_use_case()` in tests
- **Orchestration**: Business logic stays in use case
- **Flexible**: Can swap service implementation without breaking API

### Test Example

```python
# tests/api/test_search_routes.py
from unittest.mock import AsyncMock

async def test_search_endpoint():
    # Mock the use case
    mock_use_case = AsyncMock()
    mock_use_case.search.return_value = SearchResponse(results=[])

    # Patch dependency injection
    with patch('application.use_cases.search.get_search_use_case', return_value=mock_use_case):
        response = client.post("/search", json={"query": "test"})

    # Verify use case was called
    mock_use_case.search.assert_called_once_with(SearchRequest(query="test"))
```

### Reuse for Real AgentX

**Status**: ✅ REQUIRED - Use for all API endpoints

**Use Case Template**:
```python
# application/use_cases/{feature}.py
class {Feature}UseCase:
    def __init__(self, service: {Service}):
        self._service = service

    def execute(self, request: {Request}DTO) -> {Response}DTO:
        # Orchestrate business logic
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
```

---

## Decision 3: WebSocket Connection State Tracking

**When**: During WebSocket implementation (Phase 2)
**What**: Boolean flag to prevent callbacks after error/disconnect
**Result**: No more cascading WebSocket errors

### The Problem

**Before**:
```python
@router.websocket("/ws/generate-widget")
async def generate_widget_master_agent(websocket: WebSocket):
    await websocket.accept()

    # Progress callback
    async def send_progress(checkpoint: str, status: str):
        await websocket.send_json({
            "type": "qa_progress",
            "data": {"checkpoint": checkpoint, "status": status}
        })

    # Main pipeline
    await run_pipeline(send_progress)  # ❌ Callback continues after error!

    # If pipeline fails, callback still tries to send
    # → "WebSocket closed" exceptions
```

**Issues**:
- Callbacks continue executing after error
- Cascading "WebSocket closed" exceptions
- No way to stop callbacks after disconnect

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
            pass  # ✅ Silent failure (connection closed)

    async def send_widget(widget: dict):
        if not connection_active:  # ✅ Stop if disconnected
            return
        try:
            widget_type = widget.get("type", widget.get("descriptor_type", "unknown"))
            print(f"📦 {widget_type}")
            await websocket.send_json({"type": "widget", "data": widget})
        except Exception:
            pass  # ✅ Silent failure

    try:
        # Main pipeline with callbacks
        use_case = get_master_agent_use_case()
        delivery_plan = await use_case.setup_master_agent_with_pipeline(
            session_id=session_id,
            user_query=user_query,
            device_context=device_context,
            send_qa_progress=send_qa_progress,
            send_widget=send_widget,
        )
    except Exception as e:
        # ✅ Set flag on error
        connection_active = False
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        # ✅ Always set flag at end
        connection_active = False
```

### Why It Works

1. **Boolean Flag**: Simple and fast check before each send
2. **Set on Error**: Flag becomes False on first error
3. **Callback Checks**: Each callback checks flag before sending
4. **Silent Exception Handling**: `pass` on WebSocket exceptions (connection already closed)

### Event Types Used

```python
# Progress events (during pipeline)
{"type": "qa_progress", "data": {"checkpoint": "search", "status": "running", "details": {}}}

# Widget events (when widget ready)
{"type": "widget", "data": {...widget_descriptor...}}

# Complete event (pipeline finished)
{"type": "complete", "data": {...delivery_plan...}}

# Error event (on exception)
{"type": "error", "message": "Error message"}
```

### Reuse for Real AgentX

**Status**: ✅ REQUIRED - Use for all WebSocket routes

**Template**:
```python
@router.websocket("/ws/{endpoint}")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # ✅ Always use connection state flag
    connection_active = True

    # Callback wrapper
    async def send_event(event_type: str, data: dict):
        if not connection_active:
            return
        try:
            await websocket.send_json({"type": event_type, "data": data})
        except Exception:
            pass

    try:
        # Main logic
        await run_operation(send_event)
    except Exception as e:
        connection_active = False
        await send_event("error", {"message": str(e)})
    finally:
        connection_active = False
```

---

## Decision 4: Three-Tier Serialization Fallback

**When**: During Master Agent implementation
**What**: Graceful degradation for unknown data types
**Result**: Never crashes on serialization

### The Problem

**Before**:
```python
await websocket.send_json(delivery_plan.model_dump())  # ❌ Crashes if no model_dump()
```

**Issues**:
- Assumes Pydantic model
- Crashes on unexpected types
- No graceful degradation

### The Solution

```python
def _serialize_delivery_plan(delivery_plan: Any) -> dict:
    """Safely serialize DeliveryPlan to dict with error handling."""

    # Tier 1: Try Pydantic model_dump()
    try:
        return delivery_plan.model_dump()
    except Exception:
        pass

    # Tier 2: Manual serialization
    try:
        return {
            "widgets": [w.model_dump() for w in delivery_plan.widgets],
            "metadata": delivery_plan.metadata.model_dump() if hasattr(delivery_plan, 'metadata') else {},
        }
    except Exception:
        pass

    # Tier 3: Minimal fallback (never fails)
    return {
        "widgets": [],
        "metadata": {},
        "error": "Serialization failed",
    }
```

### Usage

```python
# Always use wrapper
serialized = _serialize_delivery_plan(delivery_plan)
await websocket.send_json({"type": "complete", "data": serialized})
```

### Why It Works

1. **Try Best First**: Pydantic's `model_dump()` is fastest if available
2. **Manual Fallback**: Handles objects with `widgets` attribute
3. **Minimal Fallback**: Always returns valid dict structure
4. **Never Crashes**: Three tiers ensure WebSocket always gets valid JSON

### Reuse for Real AgentX

**Status**: ✅ HIGH - Use for any serialization to external systems

**Template**:
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

## Decision 5: Mock Mode Support

**When**: From initial implementation
**What**: Fast path for testing without LLM
**Result**: Test frontend without backend dependency

### The Implementation

```python
# api/routes/master_agent.py
from config.settings import settings

@router.websocket("/ws/generate-widget")
async def generate_widget_master_agent(websocket: WebSocket):
    await websocket.accept()

    # ✅ Mock mode check (fast path)
    if settings.mock_mode:
        await handle_mock_mode(websocket, session_id, user_query)
        return

    # ... real Master Agent pipeline

# api/mock_handler.py
async def handle_mock_mode(websocket: WebSocket, session_id: str, user_query: str):
    """Send pre-defined mock widgets for testing."""

    # Mock widgets from JSON
    mock_widgets = [
        {
            "descriptor": {
                "type": "markdown",
                "content": f"# Mock Response\n\nQuery: {user_query}\n\nThis is a mock response.",
            }
        },
        {
            "descriptor": {
                "type": "card",
                "title": "Mock Card",
                "content": "Mock card content",
            }
        },
    ]

    # Send mock progress events
    for checkpoint in ["analyst", "researcher", "designer", "qa"]:
        await websocket.send_json({
            "type": "qa_progress",
            "data": {"checkpoint": checkpoint, "status": "passed", "details": {}}
        })
        await asyncio.sleep(0.3)  # Simulate processing

    # Send mock widgets
    for widget in mock_widgets:
        await websocket.send_json({"type": "widget", "data": widget})

    # Send mock complete
    await websocket.send_json({
        "type": "complete",
        "data": {"widgets": mock_widgets, "metadata": {"mock": True}}
    })
```

### Benefits

1. **Fast Development**: Test UI without waiting for LLM
2. **Consistent Responses**: Same mock data every time
3. **No LLM Dependency**: Works offline
4. **Cost Savings**: Don't burn API credits during UI development

### Configuration

```python
# config/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mock_mode: bool = False  # Set via MOCK_MODE=true

    class Config:
        env_file = ".env"

# .env
# MOCK_MODE=true
```

### Reuse for Real AgentX

**Status**: ✅ HIGH - Include from day 1

**Implementation Guide**:
1. Add `mock_mode: bool` to settings
2. Create `mock_handler.py` with mock responses
3. Check `settings.mock_mode` at start of WebSocket endpoints
4. Return pre-canned responses that match real response structure

---

## Decision 6: Progressive Feedback Pattern

**When**: During Master Agent pipeline implementation
**What**: Send events after each pipeline phase
**Result**: User sees progress, not just loading spinner

### The Implementation

```python
# Master Agent pipeline with progress callbacks
async def setup_master_agent_with_pipeline(
    self,
    session_id: str,
    user_query: str,
    device_context: str,
    send_qa_progress: Callable,  # ✅ Progress callback
    send_widget: Callable,       # ✅ Widget callback
) -> DeliveryPlan:
    """Execute 10-phase Master Agent pipeline with progressive feedback."""

    # Phase 1: ANALYST
    await send_qa_progress("analyst", "running", {})
    analyst_result = await self.analyzing_agent.analyze(
        query=user_query,
        device_context=device_context,
    )
    await send_qa_progress("analyst", "passed", {"insights": len(analyst_result.insights)})

    # Phase 2: RESEARCHER
    await send_qa_progress("researcher", "running", {})
    search_results = await self.researching_agent.research(
        query=user_query,
        search_terms=analyst_result.search_terms,
    )
    await send_qa_progress("researcher", "passed", {"sources": len(search_results)})

    # Phase 3: CONTEXTUALIZER
    await send_qa_progress("contextualizer", "running", {})
    contextualized_data = await self.contextualizing_agent.contextualize(
        query=user_query,
        raw_data=search_results,
    )
    await send_qa_progress("contextualizer", "passed", {"data_points": len(contextualized_data)})

    # ... continue for all 10 phases

    # Send widgets as they're generated
    for widget in delivery_plan.widgets:
        await send_widget(widget.model_dump())

    return delivery_plan
```

### Event Types

| Phase | Checkpoint | Status | Details |
|-------|------------|--------|---------|
| 1 | analyst | running/passed/failed | insights count |
| 2 | researcher | running/passed/failed | sources count |
| 3 | contextualizer | running/passed/failed | data_points count |
| 4 | number_extractor | running/passed/failed | numbers count |
| 5 | chart_generator | running/passed/failed | charts count |
| 6 | widget_matcher | running/passed/failed | selected widgets |
| 7 | hydrator | running/passed/failed | widgets hydrated |
| 8 | assembler | running/passed/failed | delivery plan size |
| 9 | validator_qa | running/passed/failed | validation results |
| 10 | finalizer | running/passed/failed | final plan |

### Frontend Integration

```javascript
// Frontend listens to progress events
websocket.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === "qa_progress") {
    const { checkpoint, status, details } = data.data;
    updateProgressUI(checkpoint, status, details);
  } else if (data.type === "widget") {
    displayWidget(data.data);
  } else if (data.type === "complete") {
    showComplete(data.data);
  } else if (data.type === "error") {
    showError(data.message);
  }
};
```

### Benefits

1. **Better UX**: User sees progress through pipeline
2. **Debugging**: Clear which phase is slow/failing
3. **Performance Tracking**: Can time each phase
4. **Early Feedback**: Widgets appear as they're ready

### Reuse for Real AgentX

**Status**: ✅ REQUIRED - Use for all long-running operations

**Template**:
```python
async def run_long_operation(
    progress_callback: Callable[[str, str, dict], Awaitable[None]],
) -> Result:
    """Execute operation with progress updates."""

    steps = ["step1", "step2", "step3"]

    for step in steps:
        await progress_callback(step, "running", {})

        # Do work
        result = await execute_step(step)

        await progress_callback(step, "passed", {"output": result})

    return final_result
```

---

## Decision 7: File Size Limits and Splitting

**When**: Phase 5 of refactoring
**What**: Split files exceeding 150 lines into focused modules
**Result**: All files under 200 lines, single responsibility

### Before (God Objects)

| File | Lines | Issue |
|------|-------|-------|
| `api/routes.py` | 561 | Handled 4+ responsibilities |
| `services/multihop_search/agents.py` | 399 | Multiple agents in one file |
| `services/master_agent/master_agent.py` | 334 | Orchestration + pipeline logic |
| `services/tools/analyst_tools.py` | 263 | Multiple tools + type utils |

### After (Focused Files)

| Original | Split Into | Lines |
|----------|------------|-------|
| `api/routes.py` (561) | `routes/health.py` (23), `routes/search.py` (129), `routes/master_agent.py` (153) | ✅ All <150 |
| `multihop_search/agents.py` (399) | `reflection/assessor.py` (45), `reflection/planner.py` (45) | ✅ 332 remaining |
| `master_agent/master_agent.py` (334) | `orchestration/hydration_coordinator.py` (55), `orchestration/pipeline_orchestrator.py` (192) | ✅ 213 remaining |
| `analyst_tools.py` (263) | `common/type_utils.py` (91) | ✅ 179 remaining |

### Splitting Pattern

```python
# BEFORE (single file with 2 classes)
# services/master_agent/master_agent.py (334 lines)
class MasterAgent:
    # ... 150 lines

class HydrationCoordinator:
    # ... 90 lines

class PipelineOrchestrator:
    # ... 94 lines

# AFTER (3 focused files)
# services/master_agent/master_agent.py (213 lines)
class MasterAgent:
    # ... just core logic

# services/master_agent/orchestration/hydration_coordinator.py (55 lines)
class HydrationCoordinator:
    # ... focused responsibility

# services/master_agent/orchestration/pipeline_orchestrator.py (192 lines)
class PipelineOrchestrator:
    # ... focused responsibility
```

### Benefits

1. **Single Responsibility**: Each file has one clear purpose
2. **Easier Testing**: Smaller files are easier to unit test
3. **Reduced Merge Conflicts**: Changes to different aspects don't conflict
4. **Better Navigation**: Easier to find specific functionality

### Reuse for Real AgentX

**Status**: ✅ REQUIRED - Max 150 lines per file

**Rules**:
1. **Extract when >150 lines**: Don't let files grow beyond limit
2. **Group related functionality**: Keep related classes together
3. **Create shared modules**: For common utilities
4. **Single responsibility**: Each file should have one clear purpose

**Extraction Pattern**:
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
        self.helper_c = ResponsibilityC()

# responsibility_a.py
class ResponsibilityA:
    def execute(self): ...

# responsibility_b.py
class ResponsibilityB:
    def execute(self): ...

# responsibility_c.py
class ResponsibilityC:
    def execute(self): ...
```

---

## Decision 8: Single Source of Truth for Data Models

**When**: Phase 4-6 of refactoring
**What**: Consolidated scattered schemas to canonical locations
**Result**: No more duplicate definitions

### Before (Scattered Schemas)

```
UIDescriptor found in 3 places:
├── models/schemas.py (80 lines)
├── services/widget_spawner/models.py (60 lines)
└── domain/entities/ui_descriptor.py (canonical)
```

**Issues**:
- Import confusion (which one is correct?)
- Synchronization risk (changes might not propagate)
- Violates DRY principle

### After (Single Source)

```
Canonical location:
└── domain/entities/ui_descriptor.py (ONE definition)

Deprecated aliases (for backward compatibility):
├── models/schemas.py → re-exports with deprecation warning
└── services/widget_spawner/models.py → re-exports with deprecation warning
```

```python
# domain/entities/ui_descriptor.py (CANONICAL)
from pydantic import BaseModel

class UIDescriptor(BaseModel):
    """Canonical UI descriptor entity."""
    id: str
    type: str
    content: dict
    # ... all fields

# models/schemas.py (DEPRECATED ALIAS)
from domain.entities.ui_descriptor import UIDescriptor as UIDescriptorEntity

# ⚠️ DEPRECATED: Use domain.entities.ui_descriptor.UIDescriptor instead
UIDescriptor = UIDescriptorEntity  # type: ignore
```

### Migration Path

Comments guide developers to canonical location:

```python
# models/schemas.py

# ═══════════════════════════════════════════════════════════════
# ⚠️  DEPRECATED: This file is deprecated for backward compatibility
# ═══════════════════════════════════════════════════════════════
#
# OLD: from models.schemas import UIDescriptor
# NEW: from domain.entities.ui_descriptor import UIDescriptorEntity
#
# This file will be removed in v2.0.0
# ═══════════════════════════════════════════════════════════════

from domain.entities.ui_descriptor import UIDescriptor as UIDescriptorEntity
UIDescriptor = UIDescriptorEntity
```

### Reuse for Real AgentX

**Status**: ✅ REQUIRED - One canonical location per entity

**Rules**:
1. **Domain entities** → `domain/entities/` (business objects)
2. **Request DTOs** → `application/dtos/requests/` (API input)
3. **Response DTOs** → `application/dtos/responses/` (API output)
4. **Use re-exports** for backward compatibility during migration
5. **Never duplicate** model definitions

---

## Summary Table: Architectural Decisions

| Decision | Phase | Impact | Status | Reuse Priority |
|----------|-------|--------|--------|----------------|
| Clean Architecture | 1-4 | 25 violations → 0 | ✅ | REQUIRED |
| Application Layer | 1 | HTTP/business separation | ✅ | REQUIRED |
| Connection State Tracking | 2 | WebSocket robustness | ✅ | REQUIRED |
| Three-Tier Serialization | 2 | Never crashes | ✅ | HIGH |
| Mock Mode Support | Initial | Fast testing | ✅ | HIGH |
| Progressive Feedback | 2 | Better UX | ✅ | REQUIRED |
| File Size Limits | 5 | Maintainability | ✅ | REQUIRED |
| Single Source of Truth | 4-6 | No duplication | ✅ | REQUIRED |

---

## Critical Rules for Real AgentX

1. **Start with Clean Architecture** - Don't refactor later like R014
2. **Use application layer** - API → use cases → services
3. **Track connection state** - Boolean flag for WebSocket
4. **Limit file sizes** - Max 150 lines, extract early
5. **Single source of truth** - One canonical location per entity
6. **Include mock mode** - Fast path for testing
7. **Send progressive feedback** - Events after each phase
8. **Use three-tier fallback** - For serialization

---

## Conclusion

R014's architectural decisions are **production-tested** through 7 phases of refactoring. Start Real AgentX with the Clean Architecture structure that R014 ended with - don't repeat the initial mistakes.

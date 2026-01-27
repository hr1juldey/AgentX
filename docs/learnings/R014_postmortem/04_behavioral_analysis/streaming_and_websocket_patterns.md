# Streaming and WebSocket Patterns in R014

## Summary
**Total Patterns Documented**: 7
**WebSocket Endpoints**: 3 (search, master_agent, mock_handler)
**Status**: All production-tested
**Source**: `api/routes/`, `tests/test_fix_log.md`

---

## Pattern 1: DSPy Streaming with Sync Warmup

**Location**: `services/pipeline/analyst.py`
**Status**: ✅ Working pattern
**Reuse**: REQUIRED for all DSPy streaming

### The Problem

**Attempt 1**: Direct streaming (fails silently)
```python
# Create streaming wrapper
stream = dspy.streamify(
    module,
    stream_listeners=[
        dspy.streaming.StreamListener(signature_field_name="next_thought")
    ]
)

# Use stream
for chunk in stream(question="What is AI?"):
    print(chunk, end="")

# Result: No output, hangs, or returns empty
```

**Root Cause**: DSPy's streaming requires synchronous initialization before async streaming.

### The Solution

```python
import dspy
from dspy.streaming import StreamListener

class AnalystAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.analyze = dspy.ChainOfThought(AnalyzeQuery)

    def forward(self, query: str, device_context: str = "desktop") -> dspy.Prediction:
        """Analyze query with optional streaming output."""

        # ✅ Step 1: Synchronous warmup (REQUIRED)
        _ = self.analyze(
            query="warmup",
            device_context=device_context,
        )

        # ✅ Step 2: Create streaming wrapper
        stream = dspy.streamify(
            self.analyze,
            stream_listeners=[
                StreamListener(
                    signature_field_name="next_thought",
                    allow_reuse=True,
                )
            ]
        )

        # ✅ Step 3: Stream output
        chunks = []
        for chunk in stream(query=query, device_context=device_context):
            chunks.append(chunk)

        full_result = "".join(chunks)

        return dspy.Prediction(
            domain="detected",
            query_type="analysis",
            insights=full_result,
        )
```

### Why Sync Warmup is Required

1. **DSPy Internal State**: Streaming sets up internal buffers/caches
2. **Model Initialization**: LM connection established on first call
3. **Silent Failure**: Without warmup, streaming returns empty without error

**Diagnostic Pattern**:
```python
# Symptom: Streaming returns empty
stream = dspy.streamify(module, ...)
result = ""
for chunk in stream(question="test"):
    result += chunk

if result == "":
    print("⚠️  Streaming failed - missing sync warmup")

# Fix: Add warmup call
module(question="warmup")  # Synchronous call
stream = dspy.streamify(module, ...)  # Now works
```

### Test Results

| Scenario | Without Warmup | With Warmup |
|----------|----------------|-------------|
| Simple query | Empty output ✅ | Full output ✅ |
| Complex query | Empty output ✅ | Full output ✅ |
| Multiple streams | Fails on 2nd ✅ | All work ✅ |

**Result**: Sync warmup is REQUIRED for reliable DSPy streaming.

### Reuse for Real AgentX

**Status**: ✅ REQUIRED - All DSPy streaming must use warmup

**Template**:
```python
def create_streaming_module(module: dspy.Module) -> dspy.Module:
    """Create streaming wrapper with sync warmup."""

    # Step 1: Synchronous warmup
    _ = module(query="warmup")

    # Step 2: Create streaming wrapper
    stream = dspy.streamify(
        module,
        stream_listeners=[
            StreamListener(
                signature_field_name="output_field",
                allow_reuse=True,
            )
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

## Pattern 2: WebSocket Connection State Tracking

**Location**: `api/routes/master_agent.py`, `api/routes/search.py`
**Status**: ✅ Production pattern
**Reuse**: REQUIRED for all WebSocket routes

### The Problem

**Before**: Callbacks continue after error/disconnect
```python
async def send_progress(checkpoint: str):
    await websocket.send_json({"type": "progress", "checkpoint": checkpoint})

await run_pipeline(send_progress)

# If pipeline errors, callback still tries to send
# → "WebSocket closed" exceptions cascade
```

**Issues**:
- Callbacks execute after disconnect
- Cascading "WebSocket closed" exceptions
- No way to stop callback execution

### The Solution

```python
from fastapi import WebSocket

@router.websocket("/ws/generate-widget")
async def generate_widget_master_agent(websocket: WebSocket):
    await websocket.accept()

    # ✅ Connection state flag
    connection_active = True

    # ✅ Progress callback with state check
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

    # ✅ Widget callback with state check
    async def send_widget(widget: dict):
        if not connection_active:
            return
        try:
            widget_type = widget.get("type", widget.get("descriptor_type", "unknown"))
            print(f"📦 {widget_type}")
            await websocket.send_json({"type": "widget", "data": widget})
        except Exception:
            pass

    try:
        # Main pipeline
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

1. **Boolean Flag**: Simple O(1) check before each send
2. **Set on Error**: Flag becomes False on first exception
3. **Callback Checks**: Each callback checks flag
4. **Silent Exception Handling**: `pass` on WebSocket errors

### Event Flow

```
1. WebSocket connects → connection_active = True
2. Pipeline starts → callbacks check connection_active
3. Error occurs → connection_active = False
4. Callbacks see False → return immediately (no send)
5. Finally block → connection_active = False (defensive)
```

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

## Pattern 3: Progressive Feedback Events

**Location**: `api/routes/master_agent.py`
**Status**: ✅ Production pattern
**Reuse**: REQUIRED for long-running operations

### The Implementation

**Event Types**:
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

**Pipeline Phases**:
```python
async def setup_master_agent_with_pipeline(...):
    """Execute 10-phase pipeline with progressive feedback."""

    # Phase 1: ANALYST
    await send_qa_progress("analyst", "running", {})
    analyst_result = await self.analyzing_agent.analyze(...)
    await send_qa_progress("analyst", "passed", {"insights": len(analyst_result.insights)})

    # Phase 2: RESEARCHER
    await send_qa_progress("researcher", "running", {})
    search_results = await self.researching_agent.research(...)
    await send_qa_progress("researcher", "passed", {"sources": len(search_results)})

    # ... continue for all 10 phases

    # Send widgets as they're generated
    for widget in delivery_plan.widgets:
        await send_widget(widget.model_dump())

    return delivery_plan
```

### Frontend Integration

```javascript
// Listen to progress events
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

### Checkpoint Names

| Phase | Checkpoint | Status Values | Details |
|-------|------------|---------------|---------|
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

### Reuse for Real AgentX

**Status**: ✅ REQUIRED - All long-running operations

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

## Pattern 4: Three-Tier Serialization Fallback

**Location**: `api/routes/master_agent.py`
**Status**: ✅ Production pattern
**Reuse**: HIGH for any serialization

### The Implementation

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

# Usage
serialized = _serialize_delivery_plan(delivery_plan)
await websocket.send_json({"type": "complete", "data": serialized})
```

### Why It Works

1. **Try Best First**: Pydantic's `model_dump()` fastest if available
2. **Manual Fallback**: Handles objects with known attributes
3. **Minimal Fallback**: Always returns valid dict structure
4. **Never Crashes**: Three tiers ensure WebSocket always gets valid JSON

### Test Cases

| Input Type | Tier 1 | Tier 2 | Tier 3 | Result |
|------------|--------|--------|--------|--------|
| Pydantic model | ✅ | - | - | Full dump |
| Object with widgets | ❌ | ✅ | - | Manual dump |
| Unknown type | ❌ | ❌ | ✅ | Minimal dict |

### Reuse for Real AgentX

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

## Pattern 5: Mock Mode WebSocket Handler

**Location**: `api/mock_handler.py`
**Status**: ✅ Production pattern
**Reuse**: HIGH for testing

### The Implementation

```python
# config/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mock_mode: bool = False

    class Config:
        env_file = ".env"

# api/routes/master_agent.py
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

```bash
# .env
MOCK_MODE=true
```

### Reuse for Real AgentX

**Status**: ✅ HIGH - Include from day 1

---

## Pattern 6: Session Tracking with Truncated UUID

**Location**: `api/routes/master_agent.py`, `api/routes/search.py`
**Status**: ✅ Production pattern
**Reuse**: HIGH for debugging

### The Implementation

```python
import uuid

@router.websocket("/ws/generate-widget")
async def generate_widget_master_agent(websocket: WebSocket):
    await websocket.accept()

    # Generate session ID
    session_id = uuid.uuid4().hex

    # Use first 8 chars for logs (more readable)
    session_short = session_id[:8]

    print(f"🔗 [{session_short}] WebSocket connected")

    try:
        # Pipeline with session tracking
        delivery_plan = await use_case.setup_master_agent_with_pipeline(
            session_id=session_id,
            user_query=user_query,
            device_context=device_context,
            send_qa_progress=send_qa_progress,
            send_widget=send_widget,
        )

        print(f"✅ [{session_short}] Pipeline complete")
    except Exception as e:
        print(f"❌ [{session_short}] Error: {e}")
```

**Log Output**:
```
🔗 [a3f9c2e1] WebSocket connected
✓ [a3f9c2e1] [analyst] running
✓ [a3f9c2e1] [analyst] passed
✓ [a3f9c2e1] [researcher] running
✓ [a3f9c2e1] [researcher] passed
✅ [a3f9c2e1] Pipeline complete
```

**Benefits**:
1. **Readable Logs**: 8 chars vs 32 chars
2. **Session Tracing**: Follow request through logs
3. **Debugging**: Clear which session has issues

### Reuse for Real AgentX

**Template**:
```python
import uuid

session_id = uuid.uuid4().hex
session_short = session_id[:8]
print(f"[{session_short}] Log message")
```

---

## Pattern 7: Device Context Flexibility

**Location**: `api/routes/master_agent.py`
**Status**: ✅ Production pattern
**Reuse**: HIGH for multi-device support

### The Implementation

```python
@router.websocket("/ws/generate-widget")
async def generate_widget_master_agent(websocket: WebSocket):
    await websocket.accept()

    # Accept device_context as string OR dict
    device_context_raw = (await websocket.receive_json()).get("device_context", "desktop")

    # Normalize to string
    if isinstance(device_context_raw, str):
        device_context = device_context_raw
    elif isinstance(device_context_raw, dict):
        device_context = device_context_raw.get("type", "desktop")
    else:
        device_context = "desktop"  # Default

    # Use normalized value
    delivery_plan = await use_case.setup_master_agent_with_pipeline(
        device_context=device_context,
        ...
    )
```

**Acceptable Inputs**:
- `"desktop"` ✅
- `"mobile"` ✅
- `"tablet"` ✅
- `{"type": "desktop", "width": 1920}` ✅
- `None` → defaults to `"desktop"` ✅

**Why Flexibility**:
- Frontend may send string or object
- Graceful degradation for missing data
- Clear default behavior

### Reuse for Real AgentX

**Template**:
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

## Summary Table: Streaming and WebSocket Patterns

| Pattern | Location | Status | Reuse Priority |
|---------|----------|--------|----------------|
| DSPy Sync Warmup | services/pipeline/analyst.py | ✅ | REQUIRED |
| Connection State | api/routes/master_agent.py | ✅ | REQUIRED |
| Progressive Feedback | api/routes/master_agent.py | ✅ | REQUIRED |
| Three-Tier Serialization | api/routes/master_agent.py | ✅ | HIGH |
| Mock Mode | api/mock_handler.py | ✅ | HIGH |
| Session Tracking | api/routes/*.py | ✅ | HIGH |
| Device Context Flex | api/routes/master_agent.py | ✅ | HIGH |

---

## WebSocket Event Reference

### Event Types

| Type | Purpose | Data Structure |
|------|---------|----------------|
| `qa_progress` | Pipeline progress | `{checkpoint, status, details}` |
| `widget` | Widget ready | `{widget_descriptor}` |
| `complete` | Pipeline finished | `{delivery_plan}` |
| `error` | Error occurred | `{message}` |

### Checkpoint Names

| Phase | Checkpoint | Details |
|-------|------------|---------|
| 1 | analyst | insights count |
| 2 | researcher | sources count |
| 3 | contextualizer | data_points count |
| 4 | number_extractor | numbers count |
| 5 | chart_generator | charts count |
| 6 | widget_matcher | selected widgets |
| 7 | hydrator | widgets hydrated |
| 8 | assembler | delivery plan size |
| 9 | validator_qa | validation results |
| 10 | finalizer | final plan |

### Status Values

| Status | Meaning |
|--------|---------|
| `running` | Phase in progress |
| `passed` | Phase completed successfully |
| `failed` | Phase failed (check error message) |

---

## Critical Rules for Real AgentX

1. **ALWAYS use sync warmup** - Before DSPy streaming
2. **ALWAYS track connection state** - Boolean flag for WebSocket
3. **ALWAYS send progressive feedback** - Events after each phase
4. **ALWAYS use three-tier fallback** - For serialization
5. **ALWAYS include mock mode** - For testing
6. **ALWAYS truncate session IDs** - First 8 chars for logs
7. **ALWAYS normalize device context** - Accept string or dict

---

## Conclusion

All 7 patterns are **production-tested** and working in R014. Reuse these patterns for Real AgentX WebSocket implementation.

# Function Postmortem: api/routes/master_agent.py

## Metadata
- **File**: api/routes/master_agent.py
- **Lines of Code**: 146
- **Purpose**: Master Agent WebSocket route - 10-phase generative UI pipeline
- **Dependencies**: FastAPI, application layer, mock_handler, config

---

## Functions Extracted

### generate_widget_master_agent

**Purpose**: WebSocket endpoint for Master Agent widget generation with streaming (10 phases)

**Signature**:
```python
async def generate_widget_master_agent(websocket: WebSocket) -> None
```

**Lines**: 19-146

**Complexity**: O(n) where n = number of pipeline phases (typically 8-10)

**Code Structure**:
- Lines 19-51: Connection setup, mock mode check
- Lines 53-70: Nested helper: `_serialize_delivery_plan`
- Lines 71-87: Nested helper: `send_widget`
- Lines 89-106: Nested helper: `send_qa_progress`
- Lines 108-128: Main pipeline execution
- Lines 130-145: Error handling

**Key Code Sections**:

```python
# Device Context Handling (lines 37-42)
if isinstance(device_context_raw, str):
    device_context = device_context_raw
elif isinstance(device_context_raw, dict):
    device_context = device_context_raw.get("type", "desktop")
else:
    device_context = "desktop"

# Mock Mode Shortcut (lines 49-51)
if settings.mock_mode:
    await handle_mock_mode(websocket, session_id, user_query)
    return

# Connection State Tracking (line 29)
connection_active = True
# Used to stop callbacks after error (lines 73, 91)
```

---

**Mistakes Found**:
- ⚠️ **Line 15**: Uses `__import__("fastapi").APIRouter()` instead of direct import - unusual pattern (might be for circular import avoidance)
- ⚠️ **Device context handling**: Accepts both string and dict but doesn't validate dict structure
- ⚠️ **Nested functions**: 3 nested helper functions (`_serialize_delivery_plan`, `send_widget`, `send_qa_progress`) - could be extracted to module level

**What Works**:
- ✅ **Connection state tracking**: `connection_active` flag prevents callbacks after error - elegant solution
- ✅ **Progressive feedback**: QA progress sent after each phase - great UX
- ✅ **Mock mode support**: Fast path for testing without LLM calls
- ✅ **Session tracking**: First 8 chars of UUID for readable logs
- ✅ **Graceful degradation**: Ultimate fallback in `_serialize_delivery_plan` returns minimal dict
- ✅ **Silent exception handling**: WebSocket sends wrapped in try/except with pass

**Behavioral Notes**:
- **Device Context Flexibility**: Accepts `"desktop"`, `"mobile"`, OR `{type: "desktop", ...}` - handles frontend inconsistency
- **Mock Mode**: When enabled, bypasses entire pipeline (sends pre-defined widgets from JSON)
- **Progress Events**: Sent as `{"type": "qa_progress", "data": {checkpoint, status, details}}`
- **Widget Events**: Sent as `{"type": "widget", "data": {...}}`
- **Complete Event**: Sent as `{"type": "complete", "data": {delivery_plan}}`
- **Error Event**: Sent as `{"type": "error", "message": ...}` if not already disconnected
- **Connection State**: Set to `False` on any error to stop further callback execution

**Dependencies**:
- **Imports**: `application.use_cases.master_agent`, `api.mock_handler`, `config.settings`
- **Called by**: FastAPI router on WS /ws/generate-widget
- **Calls**: `get_master_agent_use_case().setup_master_agent_with_pipeline()`
- **Nested helpers**: `_serialize_delivery_plan`, `send_widget`, `send_qa_progress`

**Refactoring Needed**:
- **MAYBE** - Extract nested functions to module level if reused elsewhere (but they're tightly coupled to this endpoint's state)
- **Consider**: Using dependency injection for device_context validation instead of isinstance checks

**WebSocket Patterns Discovered**:
1. **Connection State Pattern**: Boolean flag to stop callbacks after disconnect/error
2. **Mock Mode Pattern**: Fast path for testing without LLM (returns pre-canned responses)
3. **Progressive Feedback Pattern**: Send events after each pipeline phase
4. **Event Type Pattern**: All events have `{"type": ..., "data": ...}` structure
5. **Graceful Degradation**: Nested try/except with silent failure for closed connections

---

## Nested Helpers

### _serialize_delivery_plan

**Purpose**: Safely serialize DeliveryPlan to dict with error handling

**Signature**:
```python
def _serialize_delivery_plan(delivery_plan: Any) -> dict
```

**Lines**: 53-70

**Why Nested**: Has access to `connection_active` closure (though not used)

**Mistakes Found**:
- Uses `hasattr()` checks and `getattr()` with defaults - defensive but indicates unclear data contract
- Ultimate fallback returns minimal dict - good for robustness but suggests data model uncertainty

**What Works**:
- Three-tier fallback: model_dump() → manual serialization → minimal dict
- Handles Pydantic models, objects with widgets attribute, and unknown types
- Never raises exception - always returns serializable dict

**Behavioral Notes**:
- Tries Pydantic's `model_dump()` first (fastest if available)
- Falls back to manual widget serialization if no model_dump
- Final fallback returns empty structure - prevents WebSocket send failure

---

### send_widget

**Purpose**: Send a single widget to the frontend

**Signature**:
```python
async def send_widget(widget: dict) -> None
```

**Lines**: 71-87

**Why Nested**: Has access to `connection_active` and `websocket` closure

**What Works**:
- Checks `connection_active` before sending (stops callbacks after error)
- Extracts widget type with fallback: `widget.get("type", widget.get("descriptor_type", "unknown"))`
- Silent exception handling - if WebSocket closed, just pass

**Behavioral Notes**:
- Logs each widget sent: `📦 {widget_type}`
- Exception pass means stop sending but don't crash
- Dual key check for widget type suggests data model evolution

---

### send_qa_progress

**Purpose**: Send QA checkpoint progress to frontend

**Signature**:
```python
async def send_qa_progress(checkpoint: str, status: str, data: dict) -> None
```

**Lines**: 89-106

**Why Nested**: Has access to `connection_active` and `websocket` closure

**What Works**:
- Checks `connection_active` before sending
- Logs checkpoint progress: `✓ [{checkpoint}] {status}`
- Silent exception handling

**Behavioral Notes**:
- Status values: "running", "passed", "failed"
- Checkpoint names correspond to 10 pipeline phases
- Exception pass means stop progress updates but don't crash

---

## File Summary

**Total Functions**: 1 (with 3 nested helpers)
**Total Classes**: 0
**Lines of Code**: 146

**Violations**:
- ⚠️ Unusual import pattern: `__import__("fastapi")`
- ⚠️ Nested functions (architectural preference, not functional issue)

**Success Patterns**:
- ✅ Connection state tracking (prevents callback errors after disconnect)
- ✅ Mock mode support (enables testing without LLM)
- ✅ Progressive feedback (UX pattern for long operations)
- ✅ Graceful degradation (three-tier serialization fallback)
- ✅ Silent exception handling (WebSocket best practice)
- ✅ Session tracking with truncated UUID

**Overall Assessment**: GOOD - Well-implemented WebSocket endpoint with excellent error handling. The connection state tracking pattern is particularly elegant and should be reused in Real AgentX.

**Key Learnings for Real AgentX**:
1. ✅ **Connection State Pattern**: Use boolean flag to stop callbacks after error/disconnect
2. ✅ **Mock Mode Pattern**: Fast path for testing without LLM dependency
3. ✅ **Progressive Feedback**: Send events after each phase for better UX
4. ✅ **Silent Exception Handling**: WebSocket sends wrapped in try/except with pass
5. ✅ **Three-tier Fallback**: Try best serialization → manual → minimal
6. ⚠️ **Data Model Clarity**: Use clear contracts instead of hasattr/getattr chains
7. ⚠️ **Nested Functions**: Consider extracting to module level for testability

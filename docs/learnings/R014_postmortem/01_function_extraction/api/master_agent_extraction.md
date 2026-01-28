# master_agent.py - R014 Postmortem Extraction

**File**: `/prototypes/R014_ui_showcase/backend/api/routes/master_agent.py`
**Lines**: 146
**Purpose**: Master Agent WebSocket endpoint - main generative UI pipeline

---

## Function Catalog

| Function | Lines | Purpose |
|----------|-------|---------|
| `generate_widget_master_agent` | 126 | Main WebSocket handler for widget generation |
| `_serialize_delivery_plan` (nested) | 17 | Serialize delivery plan to dict |
| `send_widget` (nested) | 17 | Send single widget to frontend |
| `send_qa_progress` (nested) | 17 | Send QA checkpoint progress |

---

## Complete Code Structure

```python
@router.websocket("/ws/generate-widget")
async def generate_widget_master_agent(websocket: WebSocket) -> None:
    """WebSocket endpoint for Master Agent widget generation with streaming.

    Implements the complete R014 Master-Agent pipeline with 10 phases.
    """
    await websocket.accept()
    session_id = str(uuid.uuid4())[:8]

    # Track connection state to stop callbacks after error
    connection_active = True

    try:
        # Receive and validate input
        data = await websocket.receive_json()
        user_query = data.get("query", "")
        device_context_raw = data.get("device_context", "desktop")

        # Normalize device_context
        if isinstance(device_context_raw, str):
            device_context = device_context_raw
        elif isinstance(device_context_raw, dict):
            device_context = device_context_raw.get("type", "desktop")
        else:
            device_context = "desktop"

        logger.info(f"🎯 [{session_id}] {user_query[:100]}...")

        # =============================================================================
        # MOCK MODE - Send pre-defined widgets without LLM calls
        # =============================================================================
        if settings.mock_mode:
            await handle_mock_mode(websocket, session_id, user_query)
            return

        # =============================================================================
        # NESTED FUNCTION: Serialize delivery plan
        # =============================================================================
        def _serialize_delivery_plan(delivery_plan: Any) -> dict:
            """Safely serialize DeliveryPlan to dict with error handling."""
            try:
                if hasattr(delivery_plan, "model_dump"):
                    return delivery_plan.model_dump()
                # Fallback: serialize widgets manually
                return {
                    "widgets": [
                        w.model_dump() if hasattr(w, "model_dump") else w
                        for w in getattr(delivery_plan, "widgets", [])
                    ],
                    "delays": getattr(delivery_plan, "delays", []),
                    "total_duration": getattr(delivery_plan, "total_duration", 0),
                }
            except Exception:
                # Ultimate fallback: return minimal dict
                return {"widgets": [], "delays": [], "total_duration": 0}

        # =============================================================================
        # NESTED FUNCTION: Send widget to frontend
        # =============================================================================
        async def send_widget(widget: dict) -> None:
            """Send a single widget to the frontend."""
            if not connection_active:
                return
            try:
                await websocket.send_json(
                    {
                        "type": "widget",
                        "data": widget,
                    }
                )
                widget_type = widget.get(
                    "type", widget.get("descriptor_type", "unknown")
                )
                logger.info(f"  📦 {widget_type}")
            except Exception:
                pass  # WebSocket closed, stop sending

        # =============================================================================
        # NESTED FUNCTION: Send QA progress
        # =============================================================================
        async def send_qa_progress(checkpoint: str, status: str, data: dict) -> None:
            """Send QA checkpoint progress to frontend."""
            if not connection_active:
                return
            try:
                await websocket.send_json(
                    {
                        "type": "qa_progress",
                        "data": {
                            "checkpoint": checkpoint,
                            "status": status,
                            "details": data,
                        },
                    }
                )
                logger.info(f"  ✓ [{checkpoint}] {status}")
            except Exception:
                pass  # WebSocket closed, stop sending

        # =============================================================================
        # EXECUTE: Create and run master agent
        # =============================================================================
        # Use application layer use case to create and configure master agent
        use_case = get_master_agent_use_case()
        master_agent, delivery_plan_type = use_case.setup_master_agent_with_pipeline(
            widget_callback=send_widget,
            qa_callback=send_qa_progress,
        )

        delivery_plan: Any = await master_agent.execute_with_streaming(
            user_query=user_query,
            device_context=device_context,
        )

        # Send completion
        await websocket.send_json(
            {
                "type": "complete",
                "data": {
                    "delivery_plan": _serialize_delivery_plan(delivery_plan),
                },
            }
        )

        logger.info(f"✅ [{session_id}] Complete")

    except WebSocketDisconnect:
        connection_active = False
    except Exception as e:
        connection_active = False
        logger.error(f"🔴 [{session_id}] {e}", exc_info=True)
        try:
            if websocket.client_state != "disconnected":
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": str(e),
                    }
                )
        except Exception:
            pass
```

---

## Analysis

### Design Pattern: Callback Hell with Nested Functions

**Structure**:
- Outer: WebSocket handler
- Middle: Mock mode check
- Inner: 3 nested callback functions
- Core: Master agent execution

**What Works**:
- ✅ Clear flow from receive → process → send
- ✅ Connection state tracking prevents errors after disconnect
- ✅ Device context normalization handles multiple input formats
- ✅ Comprehensive error handling
- ✅ Mock mode bypass for development

**Issues**:
- ⚠️ **Nested functions** make code hard to test
- ⚠️ **Bare except: pass** hides errors
- ⚠️ **Connection state as closure** (non-obvious dependency)
- ⚠️ **No input validation** beyond `.get()`
- ⚠️ **Mixed concerns**: WebSocket + serialization + callbacks

### CLAUDE_POLICY.md Compliance

| Check | Status | Notes |
|-------|--------|-------|
| Absolute imports | ⚠️ Partial | `__import__("fastapi").APIRouter()` obfuscated |
| File size | ✅ Pass | 146 lines (<150 limit) |
| Error handling | ⚠️ Partial | Multiple `except: pass` |
| Logging | ✅ Pass | Good context logging |

### SOLID Violations

| Principle | Status | Analysis |
|-----------|--------|----------|
| Single Responsibility | ❌ Fail | WebSocket + serialization + callbacks + mock mode |
| Open/Closed | ❌ Fail | Adding new callbacks requires modification |
| Liskov Substitution | N/A | No inheritance |
| Interface Segregation | N/A | Single endpoint |
| Dependency Inversion | ❌ Fail | Directly imports use case, settings |

---

## Behavioral Notes

### LLM Interactions

1. **Master Agent Execution**:
   ```python
   delivery_plan = await master_agent.execute_with_streaming(
       user_query=user_query,
       device_context=device_context,
   )
   ```
   - Blocks until complete pipeline finishes
   - Uses callbacks for streaming updates
   - Returns delivery plan with widgets

### Edge Cases

1. **Device Context Variations**:
   ```python
   # Handles: "desktop", {"type": "mobile"}, etc.
   if isinstance(device_context_raw, str):
       device_context = device_context_raw
   elif isinstance(device_context_raw, dict):
       device_context = device_context_raw.get("type", "desktop")
   ```

2. **WebSocket Mid-Stream Disconnect**:
   - `connection_active` flag checked before each send
   - Callbacks return early if `False`
   - Exception caught silently

3. **Delivery Plan Serialization Failures**:
   - Tries `model_dump()` first
   - Falls back to manual serialization
   - Ultimate fallback: empty dict

---

## Nested Functions Analysis

### `_serialize_delivery_plan(delivery_plan)`

**Purpose**: Convert Pydantic model to dict with fallbacks.

**Issues**:
- ❌ Nested function (can't test independently)
- ❌ Triple fallback pattern suggests unclear data model
- ❌ No error logging (silent failure)

**Better**:
```python
def serialize_delivery_plan(delivery_plan: Any) -> dict:
    """Serialize delivery plan to dict."""
    if hasattr(delivery_plan, "model_dump"):
        return delivery_plan.model_dump()
    logger.warning("Using fallback serialization")
    return {"widgets": [], "delays": [], "total_duration": 0}
```

### `send_widget(widget)`

**Purpose**: Send widget to WebSocket with error suppression.

**Issues**:
- ❌ Closes over `connection_active` and `websocket`
- ❌ Silent error handling (`except: pass`)
- ❌ Can't unit test without WebSocket

**Better**:
```python
async def send_widget(
    websocket: WebSocket, 
    widget: dict, 
    connection_active: bool
) -> bool:
    """Send widget to WebSocket. Returns success."""
    if not connection_active:
        return False
    try:
        await websocket.send_json({"type": "widget", "data": widget})
        return True
    except Exception as e:
        logger.debug(f"Failed to send widget: {e}")
        return False
```

### `send_qa_progress(checkpoint, status, data)`

**Purpose**: Send QA checkpoint progress.

**Issues**:
- Same as `send_widget` (closure, silent errors)

---

## Refactoring Needed

### YES - Extract to Class

```python
class MasterAgentWebSocketHandler:
    """Handle Master Agent WebSocket connections."""
    
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.session_id = str(uuid.uuid4())[:8]
        self.connection_active = True
    
    async def handle_connection(self) -> None:
        """Main connection handler."""
        data = await self.websocket.receive_json()
        user_query = data.get("query", "")
        device_context = self._normalize_device_context(data)
        
        if settings.mock_mode:
            await self._handle_mock_mode(user_query)
            return
        
        master_agent = await self._setup_master_agent()
        delivery_plan = await self._execute_agent(master_agent, user_query, device_context)
        await self._send_completion(delivery_plan)
    
    def _normalize_device_context(self, data: dict) -> str:
        """Normalize device context from various formats."""
        # ... implementation
    
    async def send_widget(self, widget: dict) -> bool:
        """Send widget to WebSocket. Returns success."""
        # ... implementation
    
    async def send_qa_progress(self, checkpoint: str, status: str, data: dict) -> bool:
        """Send QA progress. Returns success."""
        # ... implementation
    
    @staticmethod
    def serialize_delivery_plan(delivery_plan: Any) -> dict:
        """Serialize delivery plan to dict."""
        # ... implementation
```

### YES - Remove Bare Except

```python
except Exception as e:
    logger.debug(f"WebSocket send failed: {e}")
    return False  # Don't silently ignore
```

### NO - Don't Change

- Mock mode bypass (useful for development)
- Session ID truncation (reasonable length)
- Device context normalization (good flexibility)

---

## Performance Notes

### Blocking Operations

1. **`master_agent.execute_with_streaming()`**: Blocks until complete
   - Could be slow (multiple LLM calls)
   - Callbacks provide incremental updates

2. **WebSocket sends**: Sequential (await each send)
   - Could batch widget sends
   - But streaming is intentional UX

---

## Integration Points

**Route**: `@router.websocket("/ws/generate-widget")`

**Calls**:
- `handle_mock_mode()` - If `settings.mock_mode` is True
- `get_master_agent_use_case()` - Application layer
- `master_agent.execute_with_streaming()` - Core pipeline

**Callbacks To**:
- `send_widget()` - For each generated widget
- `send_qa_progress()` - For each QA checkpoint

---

## Lessons Learned

### What Works

- Connection state tracking pattern
- Device context normalization
- Mock mode bypass for development
- Comprehensive error handling

### What Doesn't Work

- Nested functions (testing impossible)
- Bare except (hides errors)
- Mixed concerns (should be class)
- Serialization fallbacks (suggests unclear model)

### Should Copy

- Connection state flag pattern
- Session ID for logging context
- Device context normalization
- Mock mode for development

### Should Avoid

- Nested callback functions
- Bare `except: pass`
- Too many concerns in one function
- Silent failures

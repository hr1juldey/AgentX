# Function Postmortem: api/routes/master_agent.py

## Metadata
- **File**: prototypes/R014_ui_showcase/backend/api/routes/master_agent.py
- **Lines of Code**: 146
- **Purpose**: Master Agent WebSocket endpoint with streaming
- **Dependencies**: application.use_cases.master_agent, api.mock_handler, config.settings

---

## Analysis

**Status**: Working WebSocket endpoint for Master Agent pipeline

**Purpose**: Implements the complete R014 Master-Agent pipeline with 10 phases, streaming widgets and QA progress to frontend.

**Architecture**: WebSocket handler with nested callback functions

---

## Functions/Classes Extracted

### generate_widget_master_agent (websocket endpoint)

**Purpose**: WebSocket endpoint for Master Agent widget generation with streaming

**Signature**: `async def generate_widget_master_agent(websocket: WebSocket) -> None`

**Lines**: 19-145

**Key Code**:
```python
@router.websocket("/ws/generate-widget")
async def generate_widget_master_agent(websocket: WebSocket) -> None:
    await websocket.accept()
    session_id = str(uuid.uuid4())[:8]
    connection_active = True

    try:
        data = await websocket.receive_json()
        user_query = data.get("query", "")
        device_context_raw = data.get("device_context", "desktop")

        # Handle device context normalization
        if isinstance(device_context_raw, str):
            device_context = device_context_raw
        elif isinstance(device_context_raw, dict):
            device_context = device_context_raw.get("type", "desktop")
        else:
            device_context = "desktop"

        # MOCK MODE check
        if settings.mock_mode:
            await handle_mock_mode(websocket, session_id, user_query)
            return

        # Setup callbacks
        async def send_widget(widget: dict) -> None:
            if not connection_active:
                return
            try:
                await websocket.send_json({"type": "widget", "data": widget})
                logger.info(f"  📦 {widget.get('type', 'unknown')}")
            except Exception:
                pass

        async def send_qa_progress(checkpoint: str, status: str, data: dict) -> None:
            if not connection_active:
                return
            try:
                await websocket.send_json({
                    "type": "qa_progress",
                    "data": {"checkpoint": checkpoint, "status": status, "details": data},
                })
                logger.info(f"  ✓ [{checkpoint}] {status}")
            except Exception:
                pass

        # Execute master agent
        use_case = get_master_agent_use_case()
        master_agent, delivery_plan_type = use_case.setup_master_agent_with_pipeline(
            widget_callback=send_widget,
            qa_callback=send_qa_progress,
        )

        delivery_plan = await master_agent.execute_with_streaming(
            user_query=user_query,
            device_context=device_context,
        )

        await websocket.send_json({
            "type": "complete",
            "data": {"delivery_plan": _serialize_delivery_plan(delivery_plan)},
        })

    except WebSocketDisconnect:
        connection_active = False
    except Exception as e:
        connection_active = False
        logger.error(f"🔴 [{session_id}] {e}", exc_info=True)
        try:
            if websocket.client_state != "disconnected":
                await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
```

**What Works**:
- Clean WebSocket handling
- Connection state tracking prevents errors
- Mock mode integration
- Device context normalization
- Nested callbacks for streaming
- Graceful error handling

**Mistakes Found**:
- Bare except clauses in callbacks
- send_widget callback could be extracted
- No validation of user_query

**Behavioral Notes**:
- Sends widgets as they're generated
- Sends QA progress updates
- Finally sends delivery plan
- Connection state prevents errors after disconnect

**Dependencies**:
- WebSocket
- Master agent use case
- Mock handler
- Settings

**Reusability**: HIGH - Good WebSocket pattern

---

### _serialize_delivery_plan (nested function)

**Purpose**: Safely serialize DeliveryPlan to dict

**Lines**: 53-69

```python
def _serialize_delivery_plan(delivery_plan: Any) -> dict:
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
        return {"widgets": [], "delays": [], "total_duration": 0}
```

**What Works**:
- Multiple fallback strategies
- Safe error handling
- Handles both Pydantic and dict objects

**Mistakes Found**:
- Bare except catches too broadly
- Ultimate fallback returns empty data

**Reusability**: HIGH - Good serialization pattern

---

## File Summary

**Assessment**: Well-implemented WebSocket endpoint with good error handling and connection state management.

**Key Learnings**:
1. Connection state tracking prevents post-disconnect errors
2. Nested callbacks work well for streaming
3. Device context normalization handles different input formats
4. Multiple serialization fallbacks increase robustness
5. Mock mode integration simplifies testing

**Mistakes to Avoid**:
1. Don't use bare except clauses
2. Don't fail silently - log errors
3. Don't skip input validation

**Recommendations**:
1. Add specific exception handling
2. Extract callbacks to module level
3. Add query validation
4. Log all exceptions properly

**Reusability Score**: HIGH - Excellent WebSocket pattern

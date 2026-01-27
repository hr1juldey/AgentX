# Function Postmortem: api/routes/e2e_test.py

## Metadata
- **File**: prototypes/R014_ui_showcase/backend/api/routes/e2e_test.py
- **Lines of Code**: 174
- **Purpose**: Development endpoints for testing widget delivery without full pipeline
- **Dependencies**: fastapi, services.master_agent.delivery_planner, tests.e2e.mock_widget_factory

---

## Analysis

**Status**: Working E2E test routes for frontend development

**Purpose**: Provides WebSocket and REST endpoints for testing widget delivery patterns without running the full LLM pipeline.

**Architecture**: Router with WebSocket + REST endpoints

---

## Functions/Classes Extracted

### e2e_test_widget_delivery (websocket endpoint)

**Purpose**: WebSocket endpoint for E2E testing of widget delivery

**Signature**: `async def e2e_test_widget_delivery(websocket: WebSocket) -> None`

**Lines**: 20-116

**Key Code**:
```python
@router.websocket("/ws/e2e-test-widget-delivery")
async def e2e_test_widget_delivery(websocket: WebSocket) -> None:
    """WebSocket endpoint for E2E testing of widget delivery.

    Message format:
    {
        "widget_types": ["markdown", "chart", "gallery"],
        "sequence": ["markdown", "chart", "gallery"],
        "min_delay": 0.5,
        "max_delay": 1.0
    }
    """
    await websocket.accept()
    session_id = str(uuid.uuid4())[:8]
    connection_active = True

    try:
        data = await websocket.receive_json()

        widget_types = data.get("widget_types", MockWidgetFactory.WIDGET_TYPES)
        sequence = data.get("sequence", widget_types)
        min_delay = data.get("min_delay", 0.5)
        max_delay = data.get("max_delay", 1.0)

        # Create mock widgets
        widgets = [MockWidgetFactory.create_widget(t) for t in widget_types]

        # Create delivery plan
        planner = DeliveryPlanner(min_delay=min_delay, max_delay=max_delay)
        delivery_plan = planner.plan_delivery(widgets, sequence)

        # Send progress message
        await websocket.send_json({
            "type": "test_start",
            "data": {
                "widget_count": len(widgets),
                "estimated_duration": delivery_plan.total_duration,
            },
        })

        # Deliver widgets with delays
        await planner.deliver_with_delay(delivery_plan, send_widget)

        # Send completion message
        await websocket.send_json({
            "type": "complete",
            "data": {
                "delivered_count": len(widgets),
                "session_id": session_id,
            },
        })
```

**What Works**:
- Clean WebSocket handling
- Good session management
- Uses DeliveryPlanner for realistic timing
- Progress updates before delivery
- Graceful disconnect handling

**Mistakes Found**:
- send_widget is nested function - could be extracted
- No validation of widget_types
- No validation of sequence

**Behavioral Notes**:
- Accepts configuration from client
- Creates widgets using MockWidgetFactory
- Uses DeliveryPlanner for timing
- Sends test_start, widgets, then complete

**Dependencies**:
- WebSocket
- DeliveryPlanner
- MockWidgetFactory

**Reusability**: HIGH - Good test pattern

---

### send_widget (nested function)

**Purpose**: Send a single widget to frontend

**Lines**: 51-65

```python
async def send_widget(widget: dict) -> None:
    """Send a single widget to the frontend."""
    if not connection_active:
        return
    try:
        await websocket.send_json({
            "type": "widget",
            "data": widget,
        })
        widget_type = widget.get("type", "unknown")
        logger.info(f"  📦 [E2E-{session_id}] Sent {widget_type}")
    except Exception:
        pass
```

**What Works**:
- Checks connection state
- Catches exceptions silently
- Logs widget type

**Mistakes Found**:
- Bare except catches too broadly
- Silent failure hides issues

**Reusability**: MEDIUM - Could be standalone function

---

### create_mock_widgets (POST endpoint)

**Purpose**: Create mock widgets without WebSocket

**Signature**: `async def create_mock_widgets(config: dict[str, Any]) -> dict[str, Any]`

**Lines**: 119-142

```python
@router.post("/e2e/mock-widgets")
async def create_mock_widgets(config: dict[str, Any]) -> dict[str, Any]:
    """Create mock widgets for testing without WebSocket.

    Args:
        config: Configuration with keys:
            - widget_types: list of widget types to create
            - count: number of each type (default: 1)

    Returns:
        Dict with created widgets
    """
    widget_types = config.get("widget_types", ["markdown", "chart"])
    count = config.get("count", 1)

    widgets = []
    for _ in range(count):
        for wtype in widget_types:
            widgets.append(MockWidgetFactory.create_widget(wtype))

    return {
        "widgets": widgets,
        "count": len(widgets),
    }
```

**What Works**:
- Simple REST interface
- Configurable types and count
- No WebSocket required

**Mistakes Found**:
- No validation of config
- No limit on count (could be huge)

**Reusability**: HIGH - Good for quick testing

---

### get_available_widget_types (GET endpoint)

**Purpose**: Get list of available widget types

**Signature**: `async def get_available_widget_types() -> dict[str, Any]`

**Lines**: 145-155

```python
@router.get("/e2e/widget-types")
async def get_available_widget_types() -> dict[str, Any]:
    """Get list of available widget types for testing.

    Returns:
        Dict with available widget types
    """
    return {
        "widget_types": MockWidgetFactory.WIDGET_TYPES,
        "count": len(MockWidgetFactory.WIDGET_TYPES),
    }
```

**Reusability**: HIGH - Useful for frontend discovery

---

### validate_widget (POST endpoint)

**Purpose**: Validate a widget structure

**Signature**: `async def validate_widget(widget: dict[str, Any]) -> dict[str, Any]`

**Lines**: 158-173

```python
@router.post("/e2e/validate-widget")
async def validate_widget(widget: dict[str, Any]) -> dict[str, Any]:
    """Validate a widget structure.

    Args:
        widget: Widget descriptor to validate

    Returns:
        Dict with validation result
    """
    is_valid, errors = MockWidgetFactory.validate_widget_structure(widget)

    return {
        "valid": is_valid,
        "errors": errors,
    }
```

**Reusability**: HIGH - Good for debugging

---

## File Summary

**Assessment**: Excellent E2E test infrastructure. Provides both WebSocket and REST interfaces for thorough testing.

**Key Learnings**:
1. E2E endpoints enable frontend development without backend
2. DeliveryPlanner provides realistic timing simulation
3. Multiple interfaces (WebSocket + REST) increase flexibility
4. Session tracking aids debugging
5. Validation endpoints catch issues early

**Mistakes to Avoid**:
1. Don't use bare except clauses
2. Don't fail silently - log errors
3. Don't skip validation of input

**Recommendations**:
1. Extract send_widget to module level
2. Add input validation
3. Add limits on widget counts
4. Log all exceptions properly

**Reusability Score**: HIGH - Excellent test infrastructure

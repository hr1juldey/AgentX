# Function Postmortem: api/mock_handler.py

## Metadata
- **File**: prototypes/R014_ui_showcase/backend/api/mock_handler.py
- **Lines of Code**: 88
- **Purpose**: Mock mode WebSocket handler for testing without LLM calls
- **Dependencies**: json, pathlib, fastapi

---

## Analysis

**Status**: Working mock mode handler for development/testing

**Purpose**: Sends pre-defined widgets from a JSON file when MOCK_MODE is enabled, allowing frontend testing without LLM calls.

**Architecture**: Async WebSocket handler with JSON data source

---

## Functions/Classes Extracted

### MOCK_DATA_PATH (module constant)

**Purpose**: Path to mock widget data JSON file

**Lines**: 17-19

```python
MOCK_DATA_PATH = (
    Path(__file__).parent.parent / "services" / "mock_data" / "widgets.json"
)
```

**Behavioral Notes**:
- Resolved relative to this file
- Points to services/mock_data/widgets.json
- Used for mock widget definitions

---

### handle_mock_mode (async function)

**Purpose**: Handle mock mode WebSocket connection

**Signature**: `async def handle_mock_mode(websocket: WebSocket, session_id: str, query: str) -> None`

**Lines**: 22-88

**Key Code**:
```python
async def handle_mock_mode(websocket: WebSocket, session_id: str, query: str) -> None:
    """Handle mock mode - send pre-defined widgets without LLM calls.

    Args:
        websocket: WebSocket connection
        session_id: Session identifier for logging
        query: User query (for logging purposes)
    """
    try:
        if not MOCK_DATA_PATH.exists():
            await websocket.send_json(
                {"type": "error", "message": "Mock data not found"}
            )
            return

        with open(MOCK_DATA_PATH, "r") as f:
            mock_data = json.load(f)

        widgets = mock_data.get("widgets", {})
        defaults = mock_data.get(
            "delivery_defaults", {"delays": [0.0], "total_duration": 1.0}
        )

        # Prepare widgets with timestamps
        widgets_to_send = []
        for widget_data in widgets.values():
            prepared = widget_data.copy()
            if prepared.get("timestamp") == "auto":
                prepared["timestamp"] = datetime.utcnow().isoformat()
            widgets_to_send.append(prepared)

        delays = defaults["delays"][: len(widgets_to_send)]

        # Send delivery plan
        await websocket.send_json(
            {
                "type": "delivery_plan",
                "data": {
                    "widgets": widgets_to_send,
                    "delays": delays,
                    "total_duration": defaults["total_duration"],
                },
            }
        )
        logger.info(f"📦 [{session_id}] MOCK: Sending {len(widgets_to_send)} widgets")

        # Send widgets with delays
        for widget in widgets_to_send:
            await asyncio.sleep(0.5)
            await websocket.send_json({"type": "widget", "data": widget})
            logger.info(f"  📦 [{session_id}] MOCK: {widget.get('type', 'unknown')}")

        # Send completion
        await websocket.send_json(
            {"type": "complete", "data": {"total_widgets": len(widgets_to_send)}}
        )
        logger.info(f"✅ [{session_id}] MOCK: Complete")

    except Exception as e:
        logger.error(f"🔴 [{session_id}] MOCK error: {e}")
        try:
            await websocket.send_json(
                {"type": "error", "message": f"Mock mode error: {e}"}
            )
        except Exception:
            pass
```

**What Works**:
- Clean error handling with fallback
- Auto-timestamp replacement
- Delivery plan sent first
- Fixed 0.5s delay between widgets
- Good logging with emoji indicators

**Mistakes Found**:
- Fixed 0.5s delay - should use delays from JSON
- query parameter is unused (only for logging)
- No validation of widget structure
- Catches all exceptions broadly

**Behavioral Notes**:
- Sends delivery plan first with all widgets
- Then sends widgets one by one with delays
- Finally sends completion message
- Graceful error handling

**Dependencies**:
- WebSocket
- json
- pathlib
- asyncio
- datetime

**Reusability**: HIGH - Good pattern for mock mode handling

---

## File Summary

**Assessment**: Well-implemented mock mode handler. Good for development and testing without LLM dependency.

**Key Learnings**:
1. Mock mode is valuable for development/testing
2. JSON file provides easy widget customization
3. Auto-timestamp replacement is clever
4. Delivery plan pattern mirrors real pipeline
5. Graceful error handling prevents crashes

**Mistakes to Avoid**:
1. Don't ignore delays from config
2. Don't leave unused parameters
3. Don't catch exceptions too broadly
4. Don't skip validation in mock mode

**Recommendations**:
1. Use delays from delivery_defaults
2. Add widget structure validation
3. Make delay configurable
4. Add query to logs for context

**Reusability Score**: HIGH - Excellent mock mode pattern

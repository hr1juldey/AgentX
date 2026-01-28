# mock_handler.py - R014 Postmortem Extraction

**File**: `/prototypes/R014_ui_showcase/backend/api/mock_handler.py`
**Lines**: 88
**Purpose**: Mock mode WebSocket handler - sends pre-defined widgets without LLM calls

---

## Complete Code

```python
# =============================================================================
# AGENTX R014 - Mock Mode WebSocket Handler
# =============================================================================
# Sends pre-defined widgets without LLM calls when MOCK_MODE is enabled
# =============================================================================

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

from fastapi import WebSocket

logger = logging.getLogger(__name__)

MOCK_DATA_PATH = (
    Path(__file__).parent.parent / "services" / "mock_data" / "widgets.json"
)


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

---

## Function Analysis

### `handle_mock_mode(websocket, session_id, query)`

**Signature**:
```python
async def handle_mock_mode(websocket: WebSocket, session_id: str, query: str) -> None
```

**Purpose**: Send pre-defined widgets from JSON file to WebSocket without LLM calls.

**Flow**:
1. Check mock data file exists
2. Load JSON data
3. Prepare widgets with timestamps
4. Send delivery plan
5. Send widgets with delays
6. Send completion message

**Parameters**:
- `websocket`: Active WebSocket connection
- `session_id`: For logging (8-char truncated UUID)
- `query`: User query (only used for logging, not actual processing)

**Returns**: `None` (sends messages via WebSocket)

---

## Behavioral Analysis

### What Works

- ✅ Good error handling (file not found, JSON errors)
- ✅ Graceful degradation (sends error to WebSocket)
- ✅ Clear logging with emoji indicators
- ✅ Auto-timestamp generation for "auto" values
- ✅ Respects delivery plan structure (delays, duration)

### Issues

- ⚠️ **Hardcoded delay**: `await asyncio.sleep(0.5)` - not configurable
- ⚠️ **Query parameter unused**: `query` only logged, not used for filtering
- ⚠️ **Synchronous file I/O**: `with open(...)` blocks event loop
- ⚠️ **No validation**: Widget structure not validated before sending
- ⚠️ **Bare except**: `except Exception: pass` hides errors
- ⚠️ **File path calculation**: `Path(__file__).parent.parent` brittle

### CLAUDE_POLICY.md Compliance

| Check | Status | Notes |
|-------|--------|-------|
| Absolute imports | ✅ Pass | All absolute paths |
| File size | ✅ Pass | 88 lines (<150 limit) |
| No relative imports | ✅ Pass | None used |
| Error handling | ⚠️ Partial | Bare except at end |

### DRY Violations

None (single function).

---

## Edge Cases

### File Not Found
```python
if not MOCK_DATA_PATH.exists():
    await websocket.send_json({"type": "error", "message": "Mock data not found"})
    return  # Early exit
```

### Invalid JSON
```python
with open(MOCK_DATA_PATH, "r") as f:
    mock_data = json.load(f)  # May raise JSONDecodeError
```
Handled by outer `except Exception`.

### WebSocket Disconnect
```python
try:
    await websocket.send_json(...)
except Exception:
    pass  # Silently ignore disconnect during send
```

---

## Performance Notes

### Blocking Operations

1. **File I/O**: Synchronous `open()` and `json.load()` block event loop
2. **Sleep**: `asyncio.sleep(0.5)` is non-blocking (correct)
3. **JSON parsing**: Could be large (not streamed)

### Optimization Opportunities

```python
# Load mock data once at startup (caching)
_MOCK_DATA_CACHE = None

async def get_mock_data():
    global _MOCK_DATA_CACHE
    if _MOCK_DATA_CACHE is None:
        _MOCK_DATA_CACHE = json.loads(Path(...).read_text())
    return _MOCK_DATA_CACHE
```

---

## Integration Points

**Called By**:
- `api/routes/master_agent.py:50` - When `settings.mock_mode` is True

**Reads**:
- `services/mock_data/widgets.json` - Mock widget definitions

**Sends To**:
- WebSocket client (frontend)

---

## Refactoring Needed

### YES - Minor Improvements

1. **Make delay configurable**:
   ```python
   async def handle_mock_mode(
       websocket: WebSocket, 
       session_id: str, 
       query: str,
       delay: float = 0.5,  # Configurable
   ):
   ```

2. **Use async file I/O**:
   ```python
   import aiofiles
   async with aiofiles.open(MOCK_DATA_PATH, "r") as f:
       content = await f.read()
   mock_data = json.loads(content)
   ```

3. **Add widget validation**:
   ```python
   for widget in widgets_to_send:
       if not validate_widget(widget):
           logger.warning(f"Invalid widget: {widget}")
           continue
   ```

4. **Use query for filtering**:
   ```python
   # Filter widgets based on query keywords
   if query:
       widgets_to_send = [w for w in widgets if matches_query(w, query)]
   ```

### NO - Not Worth It

- Converting to class (single function is fine)
- Adding retry logic (mock mode is development-only)
- Streaming JSON (file is small)

---

## Mock Data Format

Expected structure in `widgets.json`:
```json
{
  "widgets": {
    "widget1": {
      "id": "markdown-1",
      "type": "markdown",
      "timestamp": "auto",
      "content": "# Hello World"
    }
  },
  "delivery_defaults": {
    "delays": [0.0, 0.5, 1.0],
    "total_duration": 2.0
  }
}
```

---

## Lessons Learned

### What Works

- Clean separation of mock mode from real pipeline
- Good error messages sent to frontend
- Useful for development/testing

### What Doesn't Work

- Hardcoded delays
- Unused query parameter
- Synchronous file I/O in async function

### Should Copy

- Mock mode pattern for development
- Clear error handling
- Logging with context (session_id)

### Should Avoid

- Bare `except: pass` (even for WebSocket errors)
- Synchronous I/O in async functions
- Unused function parameters

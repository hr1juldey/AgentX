# search.py - R014 Postmortem Extraction

**File**: `/prototypes/R014_ui_showcase/backend/api/routes/search.py`
**Lines**: 107
**Purpose**: Multi-hop search endpoints (REST + WebSocket)

---

## Complete Code

```python
# =============================================================================
# AGENTX R014 - Multi-Hop Search Routes
# =============================================================================

import logging
import uuid
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from application.dtos.requests import SearchRequest
from application.use_cases.search import (
    get_search_use_case,
    get_websocket_search_use_case,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/search")
async def search_endpoint(request: dict[str, Any]) -> dict[str, Any]:
    """REST endpoint for multi-hop search using application layer."""
    query = request.get("query", "")

    logger.info(f"🔍 /search called: query='{query[:50]}...'")

    try:
        use_case = get_search_use_case()
        dto_request = SearchRequest(query=query)
        answer = await use_case.search(dto_request)

        return {
            "answer": answer,
            "summary": "",
            "confidence": "medium",
            "citations": [],
            "hops": [],
            "metadata": {},
            "queries_used": [],
        }
    except Exception as e:
        logger.error(f"🔴 Error in search: {e}", exc_info=True)
        return {
            "answer": f"Error: {str(e)}",
            "summary": "",
            "confidence": "low",
            "citations": [],
            "hops": [],
            "metadata": {"error": True},
            "queries_used": [],
        }


@router.websocket("/ws/search")
async def search_websocket(websocket: WebSocket) -> None:
    """WebSocket endpoint for streaming multi-hop search progress."""
    await websocket.accept()
    session_id = str(uuid.uuid4())

    logger.info(f"🔍 WebSocket search connected: {session_id}")

    try:
        data = await websocket.receive_json()
        request = SearchRequest(**data)

        logger.info(
            f"🔍 Search request: query='{request.query[:50]}...', "
            f"max_hops={request.max_hops}"
        )

        async def send_progress(event_dict: dict[str, Any]) -> None:
            await websocket.send_json(
                {
                    "type": "hop_event",
                    "data": event_dict,
                }
            )

        use_case = get_websocket_search_use_case()
        result = await use_case.search_with_streaming(
            request=request, progress_callback=send_progress
        )

        await websocket.send_json(
            {
                "type": "final_result",
                "data": result.model_dump(),
            }
        )

        logger.info(f"🔍 Search complete: {session_id}")

    except WebSocketDisconnect:
        logger.info(f"🔍 WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"🔴 WebSocket error: {e}", exc_info=True)
        try:
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

## Function Catalog

| Function | Lines | Type | Purpose |
|----------|-------|------|---------|
| `search_endpoint` | 31 | REST | Single-shot multi-hop search |
| `search_websocket` | 66 | WebSocket | Streaming multi-hop search |
| `send_progress` (nested) | 7 | Callback | Send hop progress to client |

---

## Detailed Analysis

### `search_endpoint(request)`

**Signature**:
```python
async def search_endpoint(request: dict[str, Any]) -> dict[str, Any]
```

**Purpose**: REST endpoint for multi-hop search (non-streaming).

**Flow**:
```python
1. Extract query from request dict
2. Get use case from application layer
3. Create SearchRequest DTO
4. Call use_case.search()
5. Return response with hardcoded fields
```

**What Works**:
- ✅ Clean use of application layer
- ✅ Good error logging
- ✅ Returns error in response format

**Issues**:
- ⚠️ **Input not validated**: Accepts raw `dict` instead of Pydantic model
- ⚠️ **Hardcoded response fields**: `summary`, `confidence`, `citations`, `hops` all empty
- ⚠️ **Request type**: `dict[str, Any]` instead of proper request model
- ⚠️ **Unused fields**: Many response fields never populated

### `search_websocket(websocket)`

**Signature**:
```python
async def search_websocket(websocket: WebSocket) -> None
```

**Purpose**: WebSocket endpoint for streaming multi-hop search.

**Flow**:
```python
1. Accept WebSocket connection
2. Receive JSON data
3. Parse as SearchRequest DTO
4. Define nested callback for progress
5. Call use_case.search_with_streaming()
6. Send final result
```

**What Works**:
- ✅ Proper WebSocket lifecycle
- ✅ Streaming progress via callback
- ✅ Good logging with context

**Issues**:
- ⚠️ **Nested callback**: `send_progress` closes over websocket
- ⚠️ **No connection state**: Doesn't track if client disconnects mid-stream
- ⚠️ **Bare except**: `except Exception: pass` at end
- ⚠️ **Session ID not truncated**: Full UUID (different from master_agent)

### `send_progress(event_dict)` (Nested)

**Purpose**: Send hop event progress to WebSocket.

**Issues**:
- ❌ Nested function (can't test independently)
- ❌ Closes over `websocket`
- ❌ No error handling (uses outer try/except)

---

## Code Patterns

### REST Response Pattern

```python
# Success case:
return {
    "answer": answer,  # Only real field
    "summary": "",  # Empty
    "confidence": "medium",  # Hardcoded
    "citations": [],  # Empty
    "hops": [],  # Empty
    "metadata": {},  # Empty
    "queries_used": [],  # Empty
}

# Error case:
return {
    "answer": f"Error: {str(e)}",
    # ... all other fields empty/default
}
```

**Problems**:
1. **Only `answer` field is real** - everything else is placeholder
2. **No real citations** despite being multi-hop search
3. **No hop tracking** despite being multi-hop
4. **Suggests incomplete implementation**

### WebSocket Callback Pattern

```python
async def send_progress(event_dict: dict[str, Any]) -> None:
    await websocket.send_json({
        "type": "hop_event",
        "data": event_dict,
    })
```

**Issues**:
1. **Nested function** - can't test
2. **No error handling** - relies on outer try/except
3. **No connection check** - doesn't verify websocket is still connected

---

## Behavioral Notes

### LLM Interactions

**REST endpoint**:
- Single `use_case.search()` call
- No streaming
- No progress updates

**WebSocket endpoint**:
- `use_case.search_with_streaming()` call
- Progress callback for each hop
- Final result sent at end

### Edge Cases

1. **Empty query**: Uses `.get("query", "")` - returns empty string
2. **Invalid JSON**: Caught by outer try/except
3. **WebSocket disconnect**: Caught by `except WebSocketDisconnect`
4. **Use case failure**: Caught by outer `except Exception`

---

## CLAUDE_POLICY.md Compliance

| Check | Status | Notes |
|-------|--------|-------|
| Absolute imports | ✅ Pass | All absolute |
| File size | ✅ Pass | 107 lines (<150) |
| No relative imports | ✅ Pass | None used |
| Error handling | ⚠️ Partial | Bare except at end |

### SOLID Principles

| Principle | Status | Analysis |
|-----------|--------|----------|
| Single Responsibility | ⚠️ Partial | REST + WS in same file |
| Open/Closed | ✅ Pass | Easy to add endpoints |
| Liskov Substitution | N/A | No inheritance |
| Interface Segregation | ✅ Pass | 2 focused endpoints |
| Dependency Inversion | ✅ Pass | Depends on use case interface |

---

## DRY Violations

### Response Construction

```python
# Repeated in success and error cases:
{
    "summary": "",
    "confidence": "medium" / "low",
    "citations": [],
    "hops": [],
    "metadata": {},
    "queries_used": [],
}
```

**Could extract to**:
```python
def _create_search_response(answer: str, is_error: bool = False) -> dict:
    return {
        "answer": answer,
        "summary": "",
        "confidence": "low" if is_error else "medium",
        "citations": [],
        "hops": [],
        "metadata": {"error": is_error},
        "queries_used": [],
    }
```

---

## Refactoring Needed

### YES - Minor Improvements

1. **Use proper request models**:
   ```python
   from pydantic import BaseModel
   
   class SearchRequestModel(BaseModel):
       query: str
       max_hops: int = 3
   
   @router.post("/search")
   async def search_endpoint(request: SearchRequestModel) -> dict[str, Any]:
   ```

2. **Extract callback from nested scope**:
   ```python
   async def send_progress(
       websocket: WebSocket, 
       event: dict[str, Any]
   ) -> bool:
       try:
           await websocket.send_json({"type": "hop_event", "data": event})
           return True
       except Exception:
           return False
   
   # In handler:
   await use_case.search_with_streaming(
       request=request,
       progress_callback=lambda e: send_progress(websocket, e)
   )
   ```

3. **Add connection state tracking**:
   ```python
   connection_active = True
   
   async def send_progress(event):
       if connection_active:
           await websocket.send_json(...)
   
   try:
       # ... search code
   except WebSocketDisconnect:
       connection_active = False
   ```

4. **Populate real response fields**:
   ```python
   # Return actual hop data from use case:
   return {
       "answer": result.answer,
       "hops": result.hops,  # Real hop data
       "citations": result.citations,  # Real citations
       # ...
   }
   ```

### NO - Not Worth It

- Splitting into separate files (REST + WS related)
- Adding retry logic (use case should handle)
- Complex response builders (keep simple)

---

## Integration Points

**Route**: `/search` (REST), `/ws/search` (WebSocket)

**Calls**:
- `get_search_use_case()` - Application layer
- `get_websocket_search_use_case()` - Application layer (streaming)

**Sends**:
- Hop events (WebSocket only)
- Final results
- Error messages

---

## Lessons Learned

### What Works

- Clean use of application layer
- Proper WebSocket lifecycle
- Streaming via callback pattern
- Good error logging

### What Doesn't Work

- **Placeholder response fields** - Many empty fields
- **Nested callback** - Can't test independently
- **No connection state** - Doesn't track disconnects
- **Request as dict** - Should use Pydantic model

### Should Copy

- Application layer separation
- Callback pattern for streaming
- WebSocket error handling
- Contextual logging

### Should Avoid

- Placeholder response fields
- Nested callback functions
- Bare `except: pass`
- Request as dict instead of model

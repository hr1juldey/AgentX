# Function Postmortem: api/routes/search.py

## Metadata
- **File**: api/routes/search.py
- **Lines of Code**: 107
- **Purpose**: Multi-hop search REST and WebSocket endpoints
- **Dependencies**: FastAPI, application layer (SearchUseCase), logging, uuid

---

## Functions Extracted

### search_endpoint

**Purpose**: REST endpoint for multi-hop search using application layer

**Signature**:
```python
async def search_endpoint(request: dict[str, Any]) -> dict[str, Any]
```

**Lines**: 21-52

**Complexity**: O(1) - delegates to use case

**Code**:
```python
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
```

---

**Mistakes Found**:
- Returns hardcoded placeholder values (`summary=""`, `citations=[]`, `hops=[]`, `confidence="medium"`) instead of actual use case results
- Error handling returns error in `answer` field but still returns `confidence: "low"` instead of `error: true`

**What Works**:
- ✅ Absolute imports from application layer
- ✅ Uses DTO pattern (`SearchRequest`)
- ✅ Proper error handling with logging
- ✅ Type hints with `dict[str, Any]`
- ✅ Logging with emojis for visual clarity

**Behavioral Notes**:
- Synchronous validation of query extraction from request dict
- `request.get("query", "")` means empty string is default - might want to validate this
- Returns placeholder response structure regardless of actual search results
- Exception handling logs full stack trace (`exc_info=True`) for debugging
- Returns HTTP 200 even on error - error signaled via `metadata.error: True`

**Dependencies**:
- **Imports**: `application.dtos.requests.SearchRequest`, `application.use_cases.search.get_search_use_case`
- **Called by**: FastAPI router on POST /search
- **Calls**: `get_search_use_case().search(SearchRequest)`

**Refactoring Needed**:
- **YES (Minor)** - Return actual use case results instead of hardcoded placeholders:
  ```python
  # Should return:
  return answer.model_dump()  # or similar
  # Instead of hardcoded structure
  ```

---

### search_websocket

**Purpose**: WebSocket endpoint for streaming multi-hop search progress

**Signature**:
```python
async def search_websocket(websocket: WebSocket) -> None
```

**Lines**: 55-107

**Complexity**: O(n) where n = number of hops/events

**Code**:
```python
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
            await websocket.send_json({
                "type": "hop_event",
                "data": event_dict,
            })

        use_case = get_websocket_search_use_case()
        result = await use_case.search_with_streaming(
            request=request, progress_callback=send_progress
        )

        await websocket.send_json({
            "type": "final_result",
            "data": result.model_dump(),
        })

        logger.info(f"🔍 Search complete: {session_id}")

    except WebSocketDisconnect:
        logger.info(f"🔍 WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"🔴 WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e),
            })
        except Exception:
            pass
```

---

**Mistakes Found**:
- Nested function `send_progress` could be extracted to module level
- No validation of `SearchRequest(**data)` - could raise ValidationError if data is malformed

**What Works**:
- ✅ Excellent WebSocket pattern: accept → receive → process → send
- ✅ Proper session tracking with UUID for debugging
- ✅ Progress callback pattern for real-time updates
- ✅ Proper WebSocketDisconnect handling
- ✅ Double exception handling in error block (send might fail if connection closed)
- ✅ Absolute imports from application layer

**Behavioral Notes**:
- `await websocket.accept()` MUST be called before receiving
- `session_id` truncated to 8 chars in master_agent.py but full UUID here
- Progress callback sends events with `"type": "hop_event"` wrapper
- Final result sent with `"type": "final_result"` wrapper
- Silent exception handling in error block - if send fails, just pass (connection likely closed)
- Uses `**data` unpacking to construct SearchRequest - assumes valid structure

**Dependencies**:
- **Imports**: `application.dtos.requests.SearchRequest`, `application.use_cases.search.get_websocket_search_use_case`
- **Called by**: FastAPI router on WS /ws/search
- **Calls**: `get_websocket_search_use_case().search_with_streaming()`
- **Nested function**: `send_progress(event_dict: dict[str, Any]) -> None`

**Refactoring Needed**:
- **NO** - This is a well-implemented WebSocket endpoint
- Optional: Extract `send_progress` to module level if reused elsewhere

**WebSocket Patterns Discovered**:
1. **Session ID Pattern**: Use UUID for debugging multi-user scenarios
2. **Event Wrapper Pattern**: All messages wrapped in `{"type": ..., "data": ...}`
3. **Progress Callback Pattern**: Pass async function to use case for real-time updates
4. **Silent Error Pattern**: Double exception handling for robustness

---

## File Summary

**Total Functions**: 2 (1 REST, 1 WebSocket)
**Total Classes**: 0
**Lines of Code**: 107

**Violations**: None
**Success Patterns**:
- Application layer delegation (Clean Architecture)
- DTO pattern for type safety
- Excellent WebSocket implementation
- Progress callback pattern for streaming
- Session tracking with UUID
- Comprehensive error handling

**Overall Assessment**: GOOD - Clean WebSocket implementation with proper architectural separation. Minor improvement: return actual use case results instead of placeholders.

**Key Learnings for Real AgentX**:
1. ✅ Use progress callbacks for long-running operations
2. ✅ Wrap WebSocket events in type/data structure
3. ✅ Track sessions with UUID for debugging
4. ✅ Handle WebSocketDisconnect explicitly
5. ✅ Use double exception handling for WebSocket sends
6. ⚠️ Return actual results, not placeholders

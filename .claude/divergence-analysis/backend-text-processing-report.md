# Backend Text Processing Divergence Report

**Test Date**: 2026-02-01
**Test Type**: E2E Programmatic Request
**Backend URL**: http://localhost:8015
**Query**: "What is the capital of France?"

## Test Results

### ❌ CRITICAL FAILURE - Query Timeout (30 seconds)

The query was received by the backend but NO response was ever sent back.

### Request Flow Observed

```
1. Health Check → ✅ 200 OK (0.2s)
2. Voice Health → ✅ Available (0.2s)
3. Thread Create → ✅ 200 OK (0.2s)
4. WebSocket Connect → ✅ Connected (0.2s)
5. Status Message → ✅ Received
6. Query Message Sent → ✅ Delivered
7. Response → ❌ TIMEOUT (40s wait)
8. Connection Closed → ⚠️ "keepalive ping timeout"
```

## Log Analysis

### What WAS Logged:

```
INFO:     127.0.0.1:44822 - "WebSocket /api/v1/ws" [accepted]
DEBUG:    > TEXT '{"message_id":"...","message_type":"query",...}' [218 bytes]
DEBUG:    < PING
DEBUG:    > PONG
DEBUG:    < CLOSE 1011 (internal error) keepalive ping timeout
```

### What WAS NOT Logged (Critical):

**COMPLETELY ABSENT:**
- ❌ `[WebSocketRoutes] Connection accepted`
- ❌ `[WebSocketRoutes] Received message type: query`
- ❌ `[WebSocketRoutes] Processing query: What is the capital...`
- ❌ `[WebSocketRoutes] Executing agent query...`
- ❌ `[ExecuteAgentQuery] Starting query execution...`
- ❌ `[ExecuteAgentQuery] Session ID...`
- ❌ `[ExecuteAgentQuery] Invoking LangGraph...`
- ❌ Any agent processing logs
- ❌ Any response sending logs

## Root Cause Analysis

### Issue 1: Logging Not Working

The logging we added in `websocket_routes.py` and `execute_agent_query.py` is **NOT appearing** in the logs.

**Possible Causes:**
1. **Logger level configuration**: The loggers might be configured at a level higher than INFO
2. **Log propagation**: Loggers might not be propagating to the uvicorn handler
3. **Import issue**: The modules might not be imported/loaded correctly

**Evidence:**
- Uvicorn DEBUG logs appear (lines 12-30, 65-73)
- Pydantic warnings appear (lines 33-64)
- But NO application-level logs appear

### Issue 2: Query Processing Not Executing

Since no logs appear from the query processing flow, this suggests:

**Hypothesis A**: The `query` message type is not matching
```python
# websocket_routes.py line 56
if message.message_type.value == "query":
```

The incoming message has `"message_type": "query"` but the comparison might be failing.

**Hypothesis B**: Exception before logging
An exception might be occurring before the first log statement in `_handle_query_message()`.

**Hypothesis C**: WebSocket message parsing issue
```python
message = WebSocketMessage.from_dict(data)
```
This might be failing silently.

### Issue 3: Pydantic Serialization Warnings (Still Present)

```
PydanticSerializationUnexpectedValue(Expected 10 fields but got 5:
Expected `Message` - serialized value may not be as expected
```

**Status**: The `cache=False` setting did NOT fix this issue.

**Impact**: These warnings appear repeatedly (lines 33-64) during agent execution, suggesting the agent IS running but the responses aren't being sent back to the WebSocket.

## Most Likely Root Cause

**The agent IS executing** (evidenced by Pydantic warnings), BUT:

1. **Response is not being sent back** to the WebSocket client
2. **Logging is not configured** to show application-level logs

This suggests:
- The `ExecuteAgentQueryUseCase.execute()` is completing
- But `await websocket.send_json(response_msg.to_dict())` is either:
  - Not being called
  - Failing silently
  - The response is malformed

## Divergence from Expected Behavior

### Expected Flow:
```
Query Received → Log "Processing query" → Execute Agent → Log "Invoking LangGraph"
→ Agent Process → Log "Execution complete" → Send Response → Log "Sent response"
```

### Actual Flow:
```
Query Received → [NO LOGS] → Agent Processing (Pydantic warnings) → [NO RESPONSE]
→ WebSocket Timeout → Connection Closed
```

## Action Items

### 1. Fix Logging (CRITICAL)
```python
# In main.py or config.py, add:
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 2. Debug Message Type Matching
```python
# In websocket_routes.py, add debug log:
logger.debug(f"Received message_type: {message.message_type}")
logger.debug(f"Message type value: {message.message_type.value}")
logger.debug(f"Comparison result: {message.message_type.value == 'query'}")
```

### 3. Add Exception Logging
```python
# In _handle_query_message, wrap entire function in try/except:
try:
    logger.info(f"Starting query processing...")
    ...
except Exception as e:
    logger.error(f"Error in _handle_query_message: {e}", exc_info=True)
    raise
```

### 4. Verify Response Sending
```python
# Add log before and after send:
logger.info(f"Sending response: {len(response.response)} chars")
await websocket.send_json(response_msg.to_dict())
logger.info("Response sent successfully")
```

## Test Evidence

### Backend Log (Extract):
```
DEBUG:    < TEXT '{"message_id": "...", "message_type":"query", ...}' [218 bytes]
[Pydantic warnings appear - agent is running]
DEBUG:    < PING
DEBUG:    > PONG
DEBUG:    < CLOSE 1011 (internal error) keepalive ping timeout
```

### Client Log:
```
[2026-02-01 11:02:37.482973] Query: What is the capital of France?
[2026-02-01 11:02:37.504934] Initial message: {"status":"connected"}
[2026-02-01 11:02:37.504955] Sending query...
[40 second wait]
[2026-02-01 11:03:17.699979] Error: sent 1011 (internal error) keepalive ping timeout
```

## Conclusion

**The backend IS receiving the query and the agent IS processing** (proven by Pydantic warnings), but:

1. **No response is sent back** to the WebSocket client
2. **No application logs appear** despite comprehensive logging being added
3. **Connection times out** after 40 seconds

**This is a critical infrastructure issue** preventing text queries from working at all.

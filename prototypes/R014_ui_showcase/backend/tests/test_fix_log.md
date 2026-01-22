# R014 UI Showcase - Test Fix Log

> Ralph Loop style tracking of API documentation findings, test failures, and fixes.

## Format
- **Date**: YYYY-MM-DD
- **Test**: Test file/function name
- **Issue**: Description of failure or API issue
- **Root Cause**: Analysis of why it failed
- **Fix**: Solution applied
- **Status**: ✅ Fixed / ⚠️ Partial / ❌ Open

---

## 2026-01-22

### E2E Testing Infrastructure Setup
- **Status**: ✅ Completed

#### Created Files
1. `tests/utils/websocket_client.py` - Real WebSocket test client wrapper
2. `tests/utils/assertions.py` - Custom assertions for API validation
3. `tests/topics/test_finance_topics.py` - E2E tests for topics 1-10
4. `tests/topics/test_world_events_topics.py` - E2E tests for topics 11-20
5. `tests/streaming/test_widget_delivery.py` - WebSocket streaming tests
6. `pytest.ini` - Added `asyncio_mode = auto` for async test support
7. `main.py` - Added `reload_excludes` to exclude tests from watchfiles

#### Test Configuration
- **LLM Model**: qwen3:8b (production Ollama)
- **SearXNG**: http://192.168.1.4:8080 (real metasearch)
- **Test Approach**: Real API endpoints (no mocks)
- **Total Smoke Tests**: 13 (all passing)
- **E2E Tests**: 20 finance + 10 world events + 7 streaming tests

---

### 2026-01-22

#### Issue: Pytest async test not recognized
- **Test**: `test_complex_multistep_analytical_query`
- **Error**: `async def functions are not natively supported`
- **Root Cause**: Missing `asyncio_mode = auto` in pytest.ini
- **Fix**: Added `asyncio_mode = auto` to pytest.ini
- **Status**: ✅ Fixed

---

### 2026-01-22

#### Issue: FlowPlannerModule parameter name mismatch
- **Test**: `test_complex_multistep_analytical_query` (E2E)
- **Error**: `FlowPlannerModule.forward() got an unexpected keyword argument 'query'`
- **Location**: `services/pipeline/sequencer.py:52`
- **Root Cause**: SEQUENCER agent called `self.flow_planner(widgets=widgets, query=user_query)` but FlowPlannerModule.forward() expects `user_query` parameter
- **Fix**: Changed `query=user_query` to `user_query=user_query` in sequencer.py:52
- **Status**: ✅ Fixed
- **Discovery**: This bug was discovered by the E2E test running the full Master Agent pipeline!

---

### 2026-01-22

#### Issue: PresenterTools _is_passed AttributeError
- **Test**: `test_finance_topic_1_inflation_detailed` (E2E)
- **Error**: `AttributeError: 'Prediction' object has no attribute 'quality_score'`
- **Location**: `services/tools/presenter_tools.py:150`
- **Root Cause**: `_is_passed()` used `getattr(result, "quality_score")` without default value, raising AttributeError when LLM doesn't return that attribute
- **Fix**: Added `None` default to all getattr calls: `getattr(result, "quality_score", None)`
- **Status**: ✅ Fixed
- **Discovery**: E2E test ran for 17 minutes through 8/9 pipeline phases (7 ✅ passed, 1 ❌ failed at PRESENTER)

---

### 2026-01-22

#### Issue: WebSocket library API incompatibility
- **Test**: `test_real_server_websocket_generate_widget`, `test_real_server_websocket_search`
- **Error**: `AttributeError: module 'websockets.asyncio' has no attribute 'connect'`
- **Root Cause**: websockets 16.0 uses `websockets.connect()` not `websockets.asyncio.connect()`
- **Fix**: Updated to use `websockets.connect()` with `send(json.dumps(...))` instead of `send_json()`
- **Status**: ✅ Fixed

#### Issue: WebSocket keepalive ping timeout during long-running requests
- **Test**: `test_real_server_websocket_generate_widget`
- **Error**: `sent 1011 (internal error) keepalive ping timeout; no close frame received`
- **Root Cause**: Default 20-second keepalive ping timeout is shorter than Master Agent pipeline execution time (can take 1-5 minutes)
- **Fix**: Added `ping_interval=None` to `websockets.connect()` to disable keepalive pings
- **Status**: ✅ Fixed

#### Issue: Server not responding to HTTP/WebSocket requests
- **Test**: `test_real_server_websocket_generate_widget`
- **Error**: Opening handshake timeout, health endpoint timeout
- **Root Cause**: Server process is stuck/blocked (possibly from previous long-running request)
- **Fix**: Server restart required
- **Status**: ✅ Fixed (server restarted successfully)

#### Issue: Multi-hop search timeout with qwen3:8b model
- **Test**: `test_real_server_search`
- **Error**: `httpx.ReadTimeout` after 300 seconds (5 minutes)
- **Root Cause**: Multi-hop search with 5 hops, each involving multiple LLM calls (plan, answer, reflect) takes 3-5+ minutes with qwen3:8b model
- **Fix**: Increased timeout from 300s to 600s (10 minutes) to account for LLM processing time
- **Status**: ✅ Fixed

---

## API Documentation Notes

### Master Agent Pipeline Flow
1. ANALYST (Pass 1) → `query_type`, `domain`, `insights`
2. RESEARCHER → SearXNG search results
3. DATA CONTEXTUALIZER → Filtered, reranked results
4. ANALYST (Pass 2) → `data_completeness` (float 0-1), `needs_more_research` (bool)
5. DESIGNER → `color_scheme` (dict), `points_of_view` (list)
6. WIDGET SELECTOR → Selected widget types
7. SEQUENCER → Delivery order with timing (2-5s)
8. PRESENTER → Final polished widgets
9. HYDRATORS → Data-filled widgets
10. DELIVERY → Staggered widget delivery via WebSocket

### WebSocket Event Types
- `qa_progress`: `{checkpoint: str, status: "running"|"passed"|"failed", details: dict}`
- `widget`: `{id, type, title, content, metadata, dismissible}`
- `complete`: `{delivery_plan: {...}}`
- `error`: `{message: str}`

### Known Failure Points (from session history)

1. **LLM Response Type Mismatches** (`services/tools/analyst_tools.py`, `contextualizer_tools.py`, `designer_tools.py`)
   - **Issue**: LLM returns text ("High", "Medium") instead of numeric scores (0.85)
   - **Fix**: Added `_to_float()` and `_to_bool()` helper functions
   - **Status**: ✅ Fixed (already in code)

2. **Device Context Type Handling** (`api/routes.py:450-458`)
   - **Issue**: Frontend sends string, backend expects object
   - **Fix**: Added isinstance checking for both formats
   - **Status**: ✅ Fixed (already in code)

3. **Color Scheme Dict vs String** (`services/tools/designer_tools.py:78-89`)
   - **Issue**: LLM returns string description instead of dict
   - **Fix**: Added default scheme fallback with isinstance checks
   - **Status**: ✅ Fixed (already in code)

---

## Testing Command Reference

```bash
# Run smoke tests first
pytest tests/smoke/ -v

# Run all tests
pytest -v

# Run with coverage
pytest --cov=services --cov=api --cov-report=html

# Run specific test file
pytest tests/smoke/test_dependencies.py -v

# Run only E2E tests
pytest tests/topics/ tests/streaming/ -v

# Run excluding slow tests
pytest -m "not slow" -v
```

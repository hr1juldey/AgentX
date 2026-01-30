# Spec: api-routes

**File**: `specs/api-routes/spec.md`

**Generated**: 2026-01-29
**Change**: c003-agent-pipeline
**Issue**: CLAUDE_POLICY.md violation - file exceeded 150 line limit

---

## 1.1 Purpose

Define the REST and WebSocket API routes for the Real AgentX agent system. This spec was created to resolve a CLAUDE_POLICY.md violation where `agent_routes.py` exceeded the 150 line limit (206 lines).

---

## 1.2 Scope

**In Scope**:
- REST endpoints for agent query execution
- REST endpoints for session management
- WebSocket endpoint for real-time agent interaction
- Request/response DTOs aligned with C002 data contracts

**Out of Scope**:
- Agent implementation (covered by dspy-* specs)
- Session storage (covered by domain specs)
- WebSocket message protocols (covered by C002)

---

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-API-001 | System MUST provide POST /api/v1/agent/query for non-streaming queries | Must |
| FR-API-002 | System MUST provide GET /api/v1/agent/session/{id} for session status | Must |
| FR-API-003 | System MUST provide GET /api/v1/agent/sessions for listing sessions | Must |
| FR-API-004 | System MUST provide DELETE /api/v1/agent/session/{id} for session deletion | Must |
| FR-API-005 | System MUST provide WebSocket /api/v1/agent/ws for real-time interaction | Must |
| FR-API-006 | All route files MUST NOT exceed 150 lines per CLAUDE_POLICY.md | Must |
| FR-API-007 | Routes MUST be split by concern (REST vs WebSocket) | Must |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-API-001 | Route files MUST use absolute imports only | Must |
| NFR-API-002 | Route files MUST pass ruff check and ruff format | Must |
| NFR-API-003 | Route files MUST pass pyrefly type checking | Must |
| NFR-API-004 | WebSocket endpoint MUST handle query, ping, and unknown messages | Must |

---

## 1.4 Refactoring (CLAUDE_POLICY.md Compliance)

### Problem

Original `agent_routes.py` violated CLAUDE_POLICY.md Rule 3:
- File size: 206 lines (limit: 150 lines)
- Mixed concerns: REST endpoints + WebSocket endpoint

### Solution

Split into two focused files:

**agent_routes.py** (106 lines):
- REST endpoints only
- Query execution
- Session CRUD operations

**websocket_routes.py** (145 lines):
- WebSocket endpoint only
- Real-time message handling
- Helper functions for each message type

---

## 1.5 Data Model

### File: agentx/presentation/api/v1/agent_routes.py

```python
"""Agent API routes for Real AgentX v0.1.

REST endpoints for agent interaction.
Following FastAPI patterns from CLAUDE.md.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from agentx.application.dtos.agent_dtos import (
    ExecuteAgentQueryRequest,
    ExecuteAgentQueryResponse,
    SessionStatusDTO,
)
from agentx.application.use_cases.execute_agent_query import (
    ExecuteAgentQueryUseCase,
)
from agentx.application.mappers.agent_session_mapper import AgentSessionMapper
from agentx.core.dependencies import get_agent_session_repository

router = APIRouter()
_query_use_case = ExecuteAgentQueryUseCase()


@router.post("/query", response_model=ExecuteAgentQueryResponse)
async def execute_query(
    request: ExecuteAgentQueryRequest,
) -> ExecuteAgentQueryResponse:
    """Execute an agent query."""
    try:
        response = await _query_use_case.execute(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/session/{session_id}", response_model=SessionStatusDTO)
async def get_session_status(session_id: str) -> SessionStatusDTO:
    """Get session status."""
    session_repo = get_agent_session_repository()
    session = await session_repo.find_by_id(UUID(session_id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return AgentSessionMapper.entity_to_dto(session)


@router.get("/sessions")
async def list_sessions(
    user_id: str | None = None,
) -> list[SessionStatusDTO]:
    """List sessions."""
    session_repo = get_agent_session_repository()
    if user_id:
        sessions = await session_repo.find_by_user(user_id)
    else:
        sessions = await session_repo.find_active_sessions()
    return [AgentSessionMapper.entity_to_dto(s) for s in sessions]


@router.delete("/session/{session_id}")
async def delete_session(session_id: str) -> JSONResponse:
    """Delete a session."""
    session_repo = get_agent_session_repository()
    await session_repo.delete(UUID(session_id))
    return JSONResponse(content={"message": "Session deleted"})
```

### File: agentx/presentation/api/v1/websocket_routes.py

```python
"""WebSocket routes for Real AgentX v0.1.

WebSocket endpoint for real-time agent interaction.
Supports query streaming, voice, UI components, and tool updates.
"""

from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from agentx.application.dtos.agent_dtos import ExecuteAgentQueryRequest
from agentx.application.use_cases.execute_agent_query import (
    ExecuteAgentQueryUseCase,
)
from agentx.ui.protocols.websocket_messages import (
    ErrorMessage,
    QueryMessage,
    ResponseMessage,
    StatusMessage,
    UIComponentMessage,
    WebSocketMessage,
)

router = APIRouter()
_query_use_case = ExecuteAgentQueryUseCase()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time agent interaction."""
    await websocket.accept()

    try:
        status_msg = StatusMessage(
            status="connected", details="WebSocket connection established"
        )
        await websocket.send_json(status_msg.to_dict())

        while True:
            data = await websocket.receive_json()
            message = WebSocketMessage.from_dict(data)

            if message.message_type.value == "query":
                await _handle_query_message(websocket, message)
            elif message.message_type.value == "ping":
                await _handle_ping_message(websocket)
            else:
                await _handle_unknown_message(websocket, message)

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        error_msg = ErrorMessage(error_message=str(e))
        await websocket.send_json(error_msg.to_dict())


async def _handle_query_message(
    websocket: WebSocket, message: WebSocketMessage
) -> None:
    """Handle query message from client."""
    query_msg = QueryMessage(
        query=message.data.get("query", ""),
        session_id=message.session_id,
    )

    request = ExecuteAgentQueryRequest(
        query=query_msg.data["query"],
        session_id=str(query_msg.session_id) if query_msg.session_id else None,
    )

    response = await _query_use_case.execute(request)

    response_msg = ResponseMessage(
        content=response.response,
        session_id=UUID(response.session_id),
        is_complete=True,
    )
    await websocket.send_json(response_msg.to_dict())

    for component in response.ui_components:
        component_uuid = (
            UUID(component.component_id)
            if component.component_id != "placeholder"
            else None
        )
        ui_msg = UIComponentMessage(
            component_type=component.component_type,
            props=component.props,
            session_id=UUID(response.session_id),
            merge=component.merge,
            component_id=component_uuid,
        )
        await websocket.send_json(ui_msg.to_dict())


async def _handle_ping_message(websocket: WebSocket) -> None:
    """Handle ping message from client."""
    pong_msg = WebSocketMessage(
        message_type=WebSocketMessage.message_type.__class__("PONG"),
        session_id=UUID(int=0),
    )
    await websocket.send_json(pong_msg.to_dict())


async def _handle_unknown_message(
    websocket: WebSocket, message: WebSocketMessage
) -> None:
    """Handle unknown message type from client."""
    error_msg = ErrorMessage(
        error_message=f"Unknown message type: {message.message_type.value}"
    )
    await websocket.send_json(error_msg.to_dict())
```

---

## 1.6 API Contract

### REST Endpoints

| Method | Path | Request | Response | Status Codes |
|--------|------|---------|----------|--------------|
| POST | `/api/v1/agent/query` | `ExecuteAgentQueryRequest` | `ExecuteAgentQueryResponse` | 200, 400, 500 |
| GET | `/api/v1/agent/session/{id}` | - | `SessionStatusDTO` | 200, 404, 500 |
| GET | `/api/v1/agent/sessions?user_id={id}` | - | `list[SessionStatusDTO]` | 200, 500 |
| DELETE | `/api/v1/agent/session/{id}` | - | `{message: string}` | 200, 404, 500 |

### WebSocket Endpoint

| Path | Message Types | Direction |
|------|---------------|-----------|
| `/api/v1/agent/ws` | query, ping, pong, response, ui_component, error | Bidirectional |

---

## 1.7 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| **BR-API-001** | Each route file MUST be under 150 lines | CLAUDE_POLICY.md Rule 3 |
| **BR-API-002** | REST and WebSocket concerns MUST be separated | Code review |
| **BR-API-003** | All routes MUST use absolute imports | CLAUDE_POLICY.md Rule 1 |
| **BR-API-004** | WebSocket MUST send status message on connect | Implementation |

---

## 1.8 Acceptance Criteria

- [x] agent_routes.py under 150 lines (106 lines)
- [x] websocket_routes.py under 150 lines (145 lines)
- [x] All files pass ruff check --fix
- [x] All files pass ruff format
- [x] All files pass pyrefly check --summarize-errors
- [x] No relative imports in any file
- [x] REST endpoints functional (query, session CRUD)
- [x] WebSocket endpoint functional (query, ping, error handling)
- [x] Type conversions correct (str → UUID for WebSocket messages)

---

**Related Specs**:
- C002 data contracts - DTOs and WebSocket message schemas
- `specs/dspy-main-agent/spec.md` - Agent orchestration
- `specs/langgraph-state-machines/spec.md` - State machine integration

---

**CLAUDE_POLICY.md Compliance**:
- ✅ Rule 1.1: Absolute imports only
- ✅ Rule 2.1: Passes ruff check --fix and ruff format
- ✅ Rule 3: File size under 150 lines
- ✅ Rule 6: Post-generation self-check passed

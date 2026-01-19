# T303: Create WebSocket Streaming

**Phase**: 3
**Estimated Time**: 50 minutes
**Dependencies**: T001, T202, T302
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/ui_descriptor_contract.md` - WebSocket message types
- `lld/incremental_release_plan.md` - Phase 3: WebSocket streaming

**Description**:
Creates WebSocket endpoints for streaming agent responses and UI updates to the frontend. Implements message types and connection management.

---

## Acceptance Criteria

**Passing Criteria**:
- ui/protocols/websocket.py exists with message types
- WebSocket manager exists for connection management
- WebSocket route exists in main.py
- Supports streaming tokens, reasoning, and UI descriptors
- All WebSocket messages defined

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify files exist
test -f agentx/ui/protocols/websocket.py && echo "WebSocket protocol exists"
test -f agentx/infrastructure/external/websocket_manager.py && echo "WebSocket manager exists"

# Verify import works
python3 -c "from agentx.ui.protocols.websocket import WebSocketMessageType; print('Import OK')"
```

---

## Implementation Steps

### Step 1: Create WebSocket message types

Create file `agentx/ui/protocols/websocket.py`:

```python
"""WebSocket message types and protocols."""

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class WebSocketMessageType(str, Enum):
    """All WebSocket message types."""

    # Agent messages
    TOKEN = "token"
    REASONING_STEP = "reasoning_step"
    TOOL_CALL = "tool_call"
    STATUS_UPDATE = "status_update"

    # UI messages
    DESCRIPTOR_CREATE = "descriptor_create"
    DESCRIPTOR_UPDATE = "descriptor_update"
    DESCRIPTOR_DISMISS = "descriptor_dismiss"

    # System messages
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

    # Session messages
    SESSION_PAUSE = "session_pause"
    SESSION_RESUME = "session_resume"
    SESSION_CLOSE = "session_close"

    # Stream control
    STREAM_START = "stream_start"
    STREAM_END = "stream_end"
    STREAM_CHUNK = "stream_chunk"


class WebSocketMessage(BaseModel):
    """Base WebSocket message structure."""

    message_type: WebSocketMessageType = Field(..., description="Type of message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    session_id: str = Field(..., description="Session identifier")
    data: Dict[str, Any] = Field(default_factory=dict, description="Message payload")


class TokenMessage(WebSocketMessage):
    """Message for streaming text tokens."""

    message_type: WebSocketMessageType = WebSocketMessageType.TOKEN
    data: Dict[str, Any] = Field(default={
        "token": "",
        "is_complete": False
    })


class ReasoningStepMessage(WebSocketMessage):
    """Message for reasoning step updates."""

    message_type: WebSocketMessageType = WebSocketMessageType.REASONING_STEP
    data: Dict[str, Any] = Field(default={
        "step_number": 0,
        "thought": "",
        "action": None,
        "observation": None
    })


class ToolCallMessage(WebSocketMessage):
    """Message for tool execution updates."""

    message_type: WebSocketMessageType = WebSocketMessageType.TOOL_CALL
    data: Dict[str, Any] = Field(default={
        "tool_name": "",
        "arguments": {},
        "result": None,
        "error": None,
        "duration_ms": 0
    })


class DescriptorCreateMessage(WebSocketMessage):
    """Message for creating UI descriptor."""

    message_type: WebSocketMessageType = WebSocketMessageType.DESCRIPTOR_CREATE
    data: Dict[str, Any] = Field(default={
        "descriptor": None  # UIDescriptor as dict
    })


class DescriptorDismissMessage(WebSocketMessage):
    """Message for dismissing UI descriptor."""

    message_type: WebSocketMessageType = WebSocketMessageType.DESCRIPTOR_DISMISS
    data: Dict[str, Any] = Field(default={
        "descriptor_id": ""
    })


class ErrorMessage(WebSocketMessage):
    """Message for errors."""

    message_type: WebSocketMessageType = WebSocketMessageType.ERROR
    data: Dict[str, Any] = Field(default={
        "error_code": "",
        "error_message": "",
        "details": {}
    })
```

### Step 2: Create WebSocket connection manager

Create file `agentx/infrastructure/external/websocket_manager.py`:

```python
"""WebSocket connection manager."""

from typing import Dict, Set, Optional
from fastapi import WebSocket
from uuid import UUID

from agentx.ui.protocols.websocket import WebSocketMessage


class WebSocketManager:
    """Manages WebSocket connections for multiple sessions.

    This class tracks active WebSocket connections and provides
    methods for broadcasting messages to specific sessions.
    """

    def __init__(self):
        """Initialize WebSocket manager."""
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        """Connect a WebSocket session.

        Args:
            websocket: WebSocket connection
            session_id: Session identifier
        """
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)

    def disconnect(self, websocket: WebSocket, session_id: str) -> None:
        """Disconnect a WebSocket session.

        Args:
            websocket: WebSocket connection
            session_id: Session identifier
        """
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def send_message(
        self,
        message: WebSocketMessage,
        session_id: str
    ) -> None:
        """Send message to specific session.

        Args:
            message: Message to send
            session_id: Session identifier
        """
        if session_id not in self.active_connections:
            return

        # Remove connection if send fails
        dead_connections = set()
        for connection in self.active_connections[session_id]:
            try:
                await connection.send_json(message.dict())
            except Exception:
                dead_connections.add(connection)

        # Clean up dead connections
        for connection in dead_connections:
            self.disconnect(connection, session_id)

    async def broadcast(
        self,
        message: WebSocketMessage,
        session_ids: Optional[list[str]] = None
    ) -> None:
        """Broadcast message to multiple sessions.

        Args:
            message: Message to broadcast
            session_ids: List of session IDs (None for all)
        """
        target_sessions = session_ids or list(self.active_connections.keys())
        for session_id in target_sessions:
            await self.send_message(message, session_id)

    def get_connection_count(self, session_id: str) -> int:
        """Get number of active connections for session.

        Args:
            session_id: Session identifier

        Returns:
            Number of active connections
        """
        return len(self.active_connections.get(session_id, set()))

    def get_total_connections(self) -> int:
        """Get total number of active connections.

        Returns:
            Total connections across all sessions
        """
        return sum(len(conns) for conns in self.active_connections.values())


# Global WebSocket manager instance
_websocket_manager: Optional[WebSocketManager] = None


def get_websocket_manager() -> WebSocketManager:
    """Get or create global WebSocket manager instance.

    Returns:
        WebSocketManager singleton
    """
    global _websocket_manager
    if _websocket_manager is None:
        _websocket_manager = WebSocketManager()
    return _websocket_manager
```

### Step 3: Create WebSocket streaming route

Create file `agentx/presentation/api/websocket.py`:

```python
"""WebSocket streaming endpoints."""

from typing import Dict, Any
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from agentx.infrastructure.external.websocket_manager import get_websocket_manager
from agentx.ui.protocols.websocket import (
    WebSocketMessageType,
    WebSocketMessage,
    TokenMessage,
    DescriptorCreateMessage,
)
from agentx.application.use_cases import ExecuteAgentQueryUseCase
from agentx.application.dtos.agent_dtos import ExecuteAgentQueryCommand


router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/agent/stream")
async def websocket_agent_stream(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for streaming agent responses.

    Connect to this endpoint to receive real-time updates from the agent:
    - Reasoning steps
    - Tool calls
    - UI descriptor creation/updates
    - Token streaming

    Args:
        websocket: WebSocket connection
        session_id: Session identifier
    """
    manager = get_websocket_manager()
    await manager.connect(websocket, session_id)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")

            if message_type == "query":
                # Handle agent query
                await handle_agent_query(websocket, session_id, data)
            elif message_type == "ping":
                # Respond to ping
                await websocket.send_json({"type": "pong"})
            elif message_type == "close":
                # Client requested close
                break

    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
    except Exception as e:
        # Send error message
        error_msg = WebSocketMessage(
            message_type=WebSocketMessageType.ERROR,
            session_id=session_id,
            data={
                "error_code": "STREAM_ERROR",
                "error_message": str(e)
            }
        )
        await manager.send_message(error_msg, session_id)
        manager.disconnect(websocket, session_id)


async def handle_agent_query(
    websocket: WebSocket,
    session_id: str,
    data: Dict[str, Any]
) -> None:
    """Handle agent query with streaming response.

    Args:
        websocket: WebSocket connection
        session_id: Session identifier
        data: Query data from client
    """
    manager = get_websocket_manager()
    user_query = data.get("query", "")

    # Send stream start message
    start_msg = WebSocketMessage(
        message_type=WebSocketMessageType.STREAM_START,
        session_id=session_id,
        data={"query": user_query}
    )
    await manager.send_message(start_msg, session_id)

    try:
        # Execute query through use case
        use_case = ExecuteAgentQueryUseCase()
        command = ExecuteAgentQueryCommand(
            session_id=UUID(session_id),
            user_query=user_query,
            retrieved_context=data.get("context", "")
        )

        response = await use_case.execute(command)

        # Stream reasoning
        for i, step in enumerate(response.reasoning_steps):
            step_msg = WebSocketMessage(
                message_type=WebSocketMessageType.REASONING_STEP,
                session_id=session_id,
                data={
                    "step_number": step.step_number,
                    "thought": step.thought,
                    "action": step.action,
                    "observation": step.observation
                }
            )
            await manager.send_message(step_msg, session_id)

        # Stream tool calls
        for tool_call in response.tool_calls:
            tool_msg = WebSocketMessage(
                message_type=WebSocketMessageType.TOOL_CALL,
                session_id=session_id,
                data={
                    "tool_name": tool_call.tool_name,
                    "arguments": tool_call.arguments,
                    "result": tool_call.result
                }
            )
            await manager.send_message(tool_msg, session_id)

        # Send final answer
        final_msg = WebSocketMessage(
            message_type=WebSocketMessageType.STREAM_END,
            session_id=session_id,
            data={
                "final_answer": response.final_answer,
                "confidence_score": response.confidence_score
            }
        )
        await manager.send_message(final_msg, session_id)

    except Exception as e:
        error_msg = WebSocketMessage(
            message_type=WebSocketMessageType.ERROR,
            session_id=session_id,
            data={
                "error_code": "QUERY_ERROR",
                "error_message": str(e)
            }
        )
        await manager.send_message(error_msg, session_id)


@router.post("/descriptor/create")
async def create_ui_descriptor(data: Dict[str, Any]):
    """REST endpoint for creating UI descriptors (alternative to WebSocket).

    Args:
        data: Descriptor data

    Returns:
        Created descriptor confirmation
    """
    session_id = data.get("session_id")
    descriptor_data = data.get("descriptor")

    manager = get_websocket_manager()
    descriptor_msg = DescriptorCreateMessage(
        session_id=session_id,
        data={"descriptor": descriptor_data}
    )

    await manager.send_message(descriptor_msg, session_id)

    return JSONResponse({
        "status": "sent",
        "session_id": session_id
    })
```

### Step 4: Register WebSocket router in main.py

Update file `agentx/main.py` (add to _register_routes function):

```python
# In _register_routes function, add:
from presentation.api.websocket import router as websocket_router

app.include_router(websocket_router)
```

### Step 5: Create ui/protocols __init__.py

Create file `agentx/ui/protocols/__init__.py`:

```python
"""UI protocols and message types."""

from agentx.ui.protocols.websocket import (
    WebSocketMessageType,
    WebSocketMessage,
    TokenMessage,
    ReasoningStepMessage,
    ToolCallMessage,
    DescriptorCreateMessage,
    DescriptorDismissMessage,
    ErrorMessage,
)

__all__ = [
    "WebSocketMessageType",
    "WebSocketMessage",
    "TokenMessage",
    "ReasoningStepMessage",
    "ToolCallMessage",
    "DescriptorCreateMessage",
    "DescriptorDismissMessage",
    "ErrorMessage",
]
```

### Step 6: Create presentation/api __init__.py

Create file `agentx/presentation/api/__init__.py`:

```python
"""Presentation API layer."""
```

---

## Expected Failures & Countermeasures

### Failure: WebSocket connection rejected

**Likelihood**: Medium
**Symptoms**: WebSocket connection fails with 403 or 404

**Countermeasures**:
1. Check main.py includes WebSocket router
2. Verify router prefix is correct (/ws)
3. Check CORS middleware allows WebSocket connections
4. Ensure session_id is passed as query parameter

**Recovery Time**: 5 minutes

### Failure: Message serialization error

**Likelihood**: Low
**Symptoms**: `Pydantic ValidationError` when sending message

**Countermeasures**:
1. Ensure message.data fields match schema
2. Check all datetime fields use .isoformat()
3. Verify descriptor can be serialized to dict
4. Use model_dump() instead of dict() for Pydantic v2

**Recovery Time**: 5 minutes

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T202 agent changed
**Detection**: Use case returns different response structure
**Action**: Update handle_agent_query to use new response fields

**Recovery Time**: 10 minutes

**Scenario**: T300 descriptors changed
**Detection**: Descriptor serialization fails
**Action**: Update descriptor message handling

**Recovery Time**: 5 minutes

### Downstream Impact

**Scenario**: WebSocket message types change
**Prevention**: All WebSocketMessageType enum values are LOCKED
**Mitigation**: Update frontend clients
**Affected Tasks**: T304 (Tests), Phase 6 (Frontend)

---

## Artifacts

**Files Created**:
- `agentx/ui/protocols/websocket.py` (WebSocket messages, LOCKED)
- `agentx/infrastructure/external/websocket_manager.py` (Connection manager, LOCKED)
- `agentx/presentation/api/websocket.py` (WebSocket routes, not locked)
- `agentx/ui/protocols/__init__.py` (Package marker)
- `agentx/presentation/api/__init__.py` (Package marker)

**Files Modified**:
- `agentx/main.py` (Register WebSocket router)

**Locked APIs**:
- All WebSocketMessageType enum values
- All WebSocket message class names
- WebSocketManager class name
- All WebSocketManager method signatures

---

## Quality Gates

**Quality Checks**:
- **Check**: WebSocket files exist
  - Command: `test -f agentx/ui/protocols/websocket.py && test -f agentx/infrastructure/external/websocket_manager.py && echo "OK"`
  - Expected: `OK`
  - Required: Yes

- **Check**: WebSocket messages can be imported
  - Command: `python3 -c "from agentx.ui.protocols.websocket import WebSocketMessageType, WebSocketMessage; print('OK')"`
  - Expected: `OK`
  - Required: Yes

- **Check**: WebSocket manager can be imported
  - Command: `python3 -c "from agentx.infrastructure.external.websocket_manager import get_websocket_manager; print('OK')"`
  - Expected: `OK`
  - Required: Yes

---

## Notes

1. WebSocket uses /ws/agent/stream endpoint
2. session_id passed as query parameter
3. Client sends JSON with "type" field
4. Server streams reasoning, tools, final answer
5. Connection manager tracks all active connections
6. Dead connections auto-cleanup on send failure
7. Alternative REST endpoint for descriptor creation

---

## Completion Checklist

- [ ] websocket.py created with all message types
- [ ] websocket_manager.py created with connection tracking
- [ ] websocket.py created with streaming endpoint
- [ ] WebSocket router registered in main.py
- [ ] ui/protocols/__init__.py exports messages
- [ ] presentation/api/__init__.py created
- [ ] All imports work
- [ ] Ready for T304 (Phase 3 Tests)

---

**Task T303 is part of Phase 3: UI DSPy Agent + Descriptors**
**Locked APIs**: All WebSocket message types, WebSocketManager signatures

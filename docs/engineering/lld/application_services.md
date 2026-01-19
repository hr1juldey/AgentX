# AGENTX Application Services LLD

**Version**: 1.0.0
**Date**: 2026-01-19
**Status**: Locked
**Dependencies**: domain_model.md

---

## Table of Contents

1. [Use Cases](#1-use-cases)
2. [Commands](#2-commands)
3. [Queries](#3-queries)
4. [DTOs](#4-dtos)
5. [Mappers](#5-mappers)

---

## 1. Use Cases

### 1.1 ExecuteAgentQueryUseCase

**File**: `application/use_cases/execute_agent_query.py`

```python
from typing import Optional
from uuid import UUID

from domain.repositories.agent_session_repository import AgentSessionRepository
from agent.dspy_agents.main_react_agent import MainDSPyReActAgent
from application.services.ui_service import UIService
from application.services.memory_service import MemoryService
from application.commands.agent_commands import ExecuteAgentQueryCommand
from application.dtos.agent_dtos import ExecuteAgentQueryResponse


class ExecuteAgentQueryUseCase:
    """Execute an agent query with streaming UI updates.

    Orchestrates: Main Agent → UI Agent → Memory Service → WebSocket Streaming
    """

    def __init__(
        self,
        session_repository: AgentSessionRepository,
        main_agent: MainDSPyReActAgent,
        ui_service: UIService,
        memory_service: MemoryService
    ):
        self._session_repository = session_repository
        self._main_agent = main_agent
        self._ui_service = ui_service
        self._memory_service = memory_service

    async def execute(self, command: ExecuteAgentQueryCommand) -> ExecuteAgentQueryResponse:
        """Execute the agent query."""
        # 1. Retrieve session
        session = await self._session_repository.get_by_id(command.session_id)
        if not session:
            raise ValueError(f"Session not found: {command.session_id}")

        # 2. Retrieve context (RAG if available)
        retrieved_context = await self._memory_service.retrieve_context(
            query=command.user_query,
            user_id=session.user_id
        )

        # 3. Execute main agent (with streaming)
        result = await self._main_agent.execute(
            user_query=command.user_query,
            conversation_history=command.conversation_history,
            retrieved_context=retrieved_context,
            ui_callback=self._ui_service.create_ui_update_callback(command.session_id)
        )

        # 4. Store interaction in memory
        await self._memory_service.store_interaction(
            session_id=command.session_id,
            user_id=session.user_id,
            query=command.user_query,
            response=result.final_answer
        )

        # 5. Update session
        session.current_reasoning_step = 0
        session.update_activity()
        await self._session_repository.update(session)

        # 6. Return response
        return ExecuteAgentQueryResponse(
            session_id=command.session_id,
            reasoning_steps=result.reasoning_steps,
            ui_updates=result.ui_updates,
            final_answer=result.final_answer,
            tool_calls=result.tool_calls,
            confidence_score=result.confidence_score
        )
```

### 1.2 HandleFormInputUseCase

**File**: `application/use_cases/handle_form_input.py`

```python
from uuid import UUID
from typing import Dict, Any

from domain.repositories.ui_component_repository import UIComponentRepository
from application.services.ui_service import UIService
from application.services.agent_orchestrator import AgentOrchestrator
from application.commands.form_commands import HandleFormInputCommand
from application.dtos.form_dtos import HandleFormInputResponse


class HandleFormInputUseCase:
    """Handle form submission and resume agent execution.

    Process: Form Submit → Validate → Resume Agent → Stream Response
    """

    def __init__(
        self,
        form_repository: UIComponentRepository,
        ui_service: UIService,
        agent_orchestrator: AgentOrchestrator
    ):
        self._form_repository = form_repository
        self._ui_service = ui_service
        self._agent_orchestrator = agent_orchestrator

    async def execute(self, command: HandleFormInputCommand) -> HandleFormInputResponse:
        """Process form input."""
        # 1. Retrieve form component
        form = await self._form_repository.get_by_id(command.form_id)
        if not form:
            raise ValueError(f"Form not found: {command.form_id}")

        # 2. Validate form data
        validation_result = await self._ui_service.validate_form(
            descriptor=form.descriptor,
            data=command.form_data
        )

        if not validation_result.is_valid:
            return HandleFormInputResponse(
                form_id=command.form_id,
                success=False,
                errors=validation_result.errors
            )

        # 3. Dismiss form
        await self._form_repository.dismiss(command.form_id)

        # 4. Resume agent with form data
        agent_result = await self._agent_orchestrator.resume_after_form(
            session_id=command.session_id,
            form_data=command.form_data
        )

        return HandleFormInputResponse(
            form_id=command.form_id,
            success=True,
            agent_response=agent_result
        )
```

### 1.3 StreamUIUpdateUseCase

**File**: `application/use_cases/stream_ui_update.py`

```python
from typing import Any, Dict

from infrastructure.external.websocket_manager import WebSocketManager
from application.dtos.ui_dtos import UIUpdateEvent
from ui.protocols.websocket_messages import WebSocketMessageType


class StreamUIUpdateUseCase:
    """Stream UI updates to frontend via WebSocket."""

    def __init__(
        self,
        websocket_manager: WebSocketManager,
        ui_serializer: UISerializer
    ):
        self._websocket_manager = websocket_manager
        self._ui_serializer = ui_serializer

    async def execute(self, update: UIUpdateEvent) -> None:
        """Send UI update to frontend."""
        # Serialize UI update
        message_data = self._ui_serializer.serialize(update)

        # Determine message type
        if update.update_type == "create":
            message_type = WebSocketMessageType.DESCRIPTOR_CREATE
        elif update.update_type == "update":
            message_type = WebSocketMessageType.DESCRIPTOR_UPDATE
        elif update.update_type == "dismiss":
            message_type = WebSocketMessageType.DESCRIPTOR_DISMISS
        else:
            raise ValueError(f"Invalid update type: {update.update_type}")

        # Send via WebSocket
        await self._websocket_manager.send_message(
            session_id=update.session_id,
            message_type=message_type,
            data=message_data
        )
```

---

## 2. Commands

**File**: `application/commands/agent_commands.py`

```python
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from uuid import UUID


class ExecuteAgentQueryCommand(BaseModel):
    """Command to execute an agent query."""

    session_id: UUID
    user_query: str
    conversation_history: Optional[List[Dict[str, str]]] = None
    ui_context: Optional[Dict[str, Any]] = None
    enable_rag: bool = True
    enable_ui: bool = True


class StartSessionCommand(BaseModel):
    """Command to start a new session."""

    user_id: str
    initial_context: Optional[Dict[str, Any]] = None
```

**File**: `application/commands/form_commands.py`

```python
from pydantic import BaseModel
from typing import Dict, Any
from uuid import UUID


class HandleFormInputCommand(BaseModel):
    """Command to handle form input."""

    session_id: UUID
    form_id: UUID
    form_data: Dict[str, Any]
    submit_action: Optional[str] = None  # Custom submit action
```

**File**: `application/commands/ui_commands.py`

```python
from pydantic import BaseModel
from uuid import UUID


class DismissUIComponentCommand(BaseModel):
    """Command to dismiss a UI component."""

    session_id: UUID
    component_id: UUID


class UpdateUIComponentCommand(BaseModel):
    """Command to update a UI component."""

    session_id: UUID
    component_id: UUID
    updates: Dict[str, Any]
```

---

## 3. Queries

**File**: `application/queries/agent_queries.py`

```python
from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class GetSessionStateQuery(BaseModel):
    """Query to get session state."""

    session_id: UUID
    include_ui_components: bool = True
    include_reasoning: bool = False


class GetSessionHistoryQuery(BaseModel):
    """Query to get session history."""

    session_id: UUID
    limit: int = 50
    offset: int = 0
```

**File**: `application/queries/ui_queries.py`

```python
from pydantic import BaseModel
from uuid import UUID


class GetVisibleComponentsQuery(BaseModel):
    """Query to get visible UI components."""

    session_id: UUID
    component_type: Optional[str] = None  # Filter by type
```

---

## 4. DTOs

**File**: `application/dtos/agent_dtos.py`

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from uuid import UUID


class ReasoningStepDTO(BaseModel):
    """DTO for agent reasoning step."""

    step_number: int = Field(..., description="Step number in reasoning")
    thought: str = Field(..., description="Agent's thought process")
    action: Optional[str] = Field(None, description="Action taken")
    observation: Optional[str] = Field(None, description="Result of action")
    timestamp: str = Field(..., description="ISO format timestamp")


class ToolCallDTO(BaseModel):
    """DTO for tool call record."""

    tool_name: str = Field(..., description="Name of tool called")
    arguments: Dict[str, Any] = Field(..., description="Tool arguments")
    result: Optional[str] = Field(None, description="Tool result")
    error: Optional[str] = Field(None, description="Tool error if failed")
    duration_ms: int = Field(..., description="Execution time in milliseconds")


class ExecuteAgentQueryResponse(BaseModel):
    """Response DTO for agent query execution."""

    session_id: UUID = Field(..., description="Session ID")
    reasoning_steps: List[ReasoningStepDTO] = Field(
        default_factory=list,
        description="Agent reasoning steps"
    )
    ui_updates: List["UIUpdateDTO"] = Field(
        default_factory=list,
        description="UI component updates"
    )
    final_answer: str = Field(..., description="Final agent response")
    tool_calls: List[ToolCallDTO] = Field(
        default_factory=list,
        description="Tool calls made"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Agent confidence in response"
    )


class SessionResponseDTO(BaseModel):
    """Response DTO for session information."""

    session_id: UUID
    user_id: str
    state: str
    created_at: str
    modified_at: str
    last_activity_at: str
    current_reasoning_step: int
    total_tool_calls: int
```

**File**: `application/dtos/ui_dtos.py`

```python
from pydantic import BaseModel, Field
from typing import Dict, Any, List
from uuid import UUID
from enum import Enum


class UIUpdateType(str, Enum):
    """Types of UI updates."""

    CREATE = "create"
    UPDATE = "update"
    DISMISS = "dismiss"


class UIUpdateDTO(BaseModel):
    """DTO for UI component update."""

    update_type: UIUpdateType = Field(..., description="Type of update")
    descriptor: Dict[str, Any] = Field(..., description="UI descriptor data")
    component_id: Optional[UUID] = Field(None, description="Component ID for updates/dismissals")


class UIUpdateEvent(BaseModel):
    """Event for UI update streaming."""

    session_id: UUID
    update_type: UIUpdateType
    descriptor: Dict[str, Any]
    timestamp: str
```

**File**: `application/dtos/form_dtos.py`

```python
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from uuid import UUID


class HandleFormInputResponse(BaseModel):
    """Response DTO for form input handling."""

    form_id: UUID
    success: bool
    errors: Optional[List[str]] = None
    agent_response: Optional[ExecuteAgentQueryResponse] = None


class FormValidationResult(BaseModel):
    """Result of form validation."""

    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
```

---

## 5. Mappers

### 5.1 AgentSessionMapper

**File**: `application/mappers/agent_session_mapper.py`

```python
from uuid import UUID
from datetime import datetime

from domain.entities.agent_session import AgentSessionEntity
from application.commands.agent_commands import StartSessionCommand
from application.dtos.agent_dtos import SessionResponseDTO


class AgentSessionMapper:
    """Mapper for AgentSessionEntity."""

    @staticmethod
    def command_to_entity(command: StartSessionCommand, session_id: UUID) -> AgentSessionEntity:
        """Convert start session command to entity."""
        now = datetime.utcnow()
        return AgentSessionEntity(
            session_id=session_id,
            user_id=command.user_id,
            state=SessionState.INITIALIZING,
            created_at=now,
            modified_at=now,
            last_activity_at=now,
            current_reasoning_step=0,
            total_tool_calls=0,
        )

    @staticmethod
    def entity_to_dto(entity: AgentSessionEntity) -> SessionResponseDTO:
        """Convert entity to response DTO."""
        return SessionResponseDTO(
            session_id=entity.session_id,
            user_id=entity.user_id,
            state=entity.state.value,
            created_at=entity.created_at.isoformat(),
            modified_at=entity.modified_at.isoformat(),
            last_activity_at=entity.last_activity_at.isoformat(),
            current_reasoning_step=entity.current_reasoning_step,
            total_tool_calls=entity.total_tool_calls,
        )
```

### 5.2 UIComponentMapper

**File**: `application/mappers/ui_component_mapper.py`

```python
from uuid import UUID
from datetime import datetime

from domain.entities.ui_component import UIComponentEntity
from ui.descriptors.base import BaseUIDescriptor
from application.dtos.ui_dtos import UIUpdateDTO, UIUpdateType


class UIComponentMapper:
    """Mapper for UIComponentEntity."""

    @staticmethod
    def descriptor_to_entity(
        descriptor: BaseUIDescriptor,
        component_id: UUID,
        session_id: UUID
    ) -> UIComponentEntity:
        """Convert descriptor to entity."""
        now = datetime.utcnow()
        return UIComponentEntity(
            component_id=component_id,
            session_id=session_id,
            component_type=UIComponentType(descriptor.descriptor_type.value),
            state=UIComponentState.CREATING,
            descriptor=descriptor,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def entity_to_update_dto(entity: UIComponentEntity, update_type: UIUpdateType) -> UIUpdateDTO:
        """Convert entity to UI update DTO."""
        return UIUpdateDTO(
            update_type=update_type,
            descriptor=entity.descriptor.model_dump(),
            component_id=entity.component_id,
        )
```

### 5.3 ToolCallMapper

**File**: `application/mappers/tool_call_mapper.py`

```python
from datetime import datetime
from typing import Dict, Any, Optional

from domain.value_objects.tool_call import ToolCall
from application.dtos.agent_dtos import ToolCallDTO


class ToolCallMapper:
    """Mapper for ToolCall value object."""

    @staticmethod
    def entity_to_dto(entity: ToolCall) -> ToolCallDTO:
        """Convert entity to DTO."""
        return ToolCallDTO(
            tool_name=entity.tool_name,
            arguments=entity.arguments,
            result=entity.result,
            error=entity.error,
            duration_ms=entity.duration_ms,
        )

    @staticmethod
    def dto_to_entity(dto: ToolCallDTO) -> ToolCall:
        """Convert DTO to entity."""
        return ToolCall(
            tool_name=dto.tool_name,
            arguments=dto.arguments,
            result=dto.result,
            error=dto.error,
            duration_ms=dto.duration_ms,
            timestamp=datetime.utcnow(),
        )
```

---

**This application services document is part of AGENTX LLD v1.0. All names and types are locked.**

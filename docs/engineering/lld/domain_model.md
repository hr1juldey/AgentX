# AGENTX Domain Model LLD

**Version**: 1.0.0
**Date**: 2026-01-19
**Status**: Locked
**Dependencies**: None (Foundation layer)

---

## Table of Contents

1. [Entities](#1-entities)
2. [Value Objects](#2-value-objects)
3. [Enums](#3-enums)
4. [Repository Interfaces](#4-repository-interfaces)
5. [Domain Services](#5-domain-services)
6. [Invariants](#6-invariants)

---

## 1. Entities

### 1.1 AgentSessionEntity

**File**: `domain/entities/agent_session.py`

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID
from typing import Optional

from domain.entities.enums import SessionState


@dataclass
class AgentSessionEntity:
    """Represents a user's conversation session with the AI agent.

    Lifecycle: INITIALIZING -> ACTIVE -> PAUSED/CLOSED
    """

    # Identity
    session_id: UUID
    user_id: str  # SHA-256 hash

    # State
    state: SessionState
    created_at: datetime
    modified_at: datetime
    last_activity_at: datetime

    # Session metadata
    current_reasoning_step: int = 0
    total_tool_calls: int = 0

    # Business methods
    def is_active(self) -> bool:
        """Check if session is in active state."""
        return self.state == SessionState.ACTIVE

    def is_paused(self) -> bool:
        """Check if session is paused."""
        return self.state == SessionState.PAUSED

    def is_closed(self) -> bool:
        """Check if session is closed."""
        return self.state == SessionState.CLOSED

    def pause(self) -> None:
        """Pause the session."""
        if self.state != SessionState.ACTIVE:
            raise ValueError(f"Cannot pause session in state: {self.state}")
        self.state = SessionState.PAUSED
        self._update_timestamp()

    def resume(self) -> None:
        """Resume a paused session."""
        if self.state != SessionState.PAUSED:
            raise ValueError(f"Cannot resume session in state: {self.state}")
        self.state = SessionState.ACTIVE
        self._update_timestamp()

    def close(self) -> None:
        """Close the session."""
        if self.state == SessionState.CLOSED:
            raise ValueError("Session is already closed")
        self.state = SessionState.CLOSED
        self._update_timestamp()

    def increment_reasoning_step(self) -> None:
        """Increment the reasoning step counter."""
        self.current_reasoning_step += 1
        self._update_timestamp()

    def increment_tool_calls(self) -> None:
        """Increment the tool call counter."""
        self.total_tool_calls += 1
        self._update_timestamp()

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity_at = datetime.utcnow()

    def _update_timestamp(self) -> None:
        """Internal: Update modified timestamp."""
        self.modified_at = datetime.utcnow()
        self.update_activity()
```

### 1.2 UIComponentEntity

**File**: `domain/entities/ui_component.py`

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID
from typing import Optional, Dict, Any

from domain.entities.enums import UIComponentType, UIComponentState
from ui.descriptors.base import BaseUIDescriptor


@dataclass
class UIComponentEntity:
    """Represents a UI component (widget) in the user interface.

    Lifecycle: CREATING -> CREATED -> UPDATING -> DISMISSED
    """

    # Identity
    component_id: UUID
    session_id: UUID

    # Component definition
    component_type: UIComponentType
    state: UIComponentState
    descriptor: BaseUIDescriptor

    # Timestamps
    created_at: datetime
    updated_at: datetime
    dismissed_at: Optional[datetime] = None

    # Business methods
    def is_dismissible(self) -> bool:
        """Check if component can be dismissed."""
        return self.descriptor.dismissible and self.state != UIComponentState.DISMISSED

    def dismiss(self) -> None:
        """Dismiss the component."""
        if not self.is_dismissible():
            raise ValueError("Component is not dismissible")
        self.state = UIComponentState.DISMISSED
        self.dismissed_at = datetime.utcnow()

    def update_descriptor(self, new_descriptor: BaseUIDescriptor) -> None:
        """Update the component descriptor."""
        if self.state == UIComponentState.DISMISSED:
            raise ValueError("Cannot update dismissed component")
        if new_descriptor.descriptor_type != self.component_type:
            raise ValueError("Descriptor type mismatch")
        self.descriptor = new_descriptor
        self.state = UIComponentState.UPDATING
        self.updated_at = datetime.utcnow()

    def mark_created(self) -> None:
        """Mark component as created."""
        if self.state != UIComponentType.CREATING:
            raise ValueError(f"Cannot mark {self.state} as created")
        self.state = UIComponentState.CREATED
        self.updated_at = datetime.utcnow()

    def is_visible(self) -> bool:
        """Check if component should be visible to user."""
        return self.state in {
            UIComponentState.CREATED,
            UIComponentState.UPDATING,
        }

    def age_seconds(self) -> int:
        """Get component age in seconds."""
        return (datetime.utcnow() - self.created_at).total_seconds()
```

### 1.3 MemoryConsolidationEntity

**File**: `domain/entities/memory_consolidation.py`

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID
from typing import Optional


@dataclass
class MemoryConsolidationEntity:
    """Represents a memory consolidation operation.

    Consolidation moves memories from Tier 2 (Agent's Qdrant) to Tier 3 (User's Qdrant + Mem0AI).
    """

    # Identity
    consolidation_id: UUID
    session_id: UUID

    # Consolidation control
    trigger: ConsolidationTrigger
    status: ConsolidationStatus

    # Timestamps
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Results
    memories_processed: int = 0
    memories_merged: int = 0
    memories_invalidated: int = 0
    error_message: Optional[str] = None

    # Business methods
    def start(self) -> None:
        """Mark consolidation as started."""
        if self.status != ConsolidationStatus.PENDING:
            raise ValueError(f"Cannot start consolidation in state: {self.status}")
        self.status = ConsolidationStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()

    def complete(
        self,
        processed: int,
        merged: int,
        invalidated: int
    ) -> None:
        """Mark consolidation as completed."""
        if self.status != ConsolidationStatus.IN_PROGRESS:
            raise ValueError(f"Cannot complete consolidation in state: {self.status}")
        self.status = ConsolidationStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.memories_processed = processed
        self.memories_merged = merged
        self.memories_invalidated = invalidated

    def fail(self, error: str) -> None:
        """Mark consolidation as failed."""
        if self.status == ConsolidationStatus.COMPLETED:
            raise ValueError("Cannot fail completed consolidation")
        self.status = ConsolidationStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error

    def duration_seconds(self) -> Optional[int]:
        """Get consolidation duration in seconds."""
        if not self.started_at or not self.completed_at:
            return None
        return (self.completed_at - self.started_at).total_seconds()

    def merge_rate(self) -> float:
        """Calculate merge rate (merged / processed)."""
        if self.memories_processed == 0:
            return 0.0
        return self.memories_merged / self.memories_processed
```

---

## 2. Value Objects

### 2.1 SHA256Hash

**File**: `domain/value_objects/sha256_hash.py`

```python
from dataclasses import dataclass
import hashlib


@dataclass(frozen=True)
class SHA256Hash:
    """Immutable SHA-256 hash value object."""

    value: str

    def __post_init__(self) -> None:
        """Validate SHA-256 hash format."""
        if not isinstance(self.value, str):
            raise TypeError("SHA256Hash value must be string")
        if len(self.value) != 64:
            raise ValueError("SHA256Hash must be 64 characters")
        if not all(c in "0123456789abcdef" for c in self.value):
            raise ValueError("SHA256Hash must be hexadecimal")

    @staticmethod
    def hash(input_string: str) -> "SHA256Hash":
        """Create SHA-256 hash from input string."""
        hash_bytes = hashlib.sha256(input_string.encode()).hexdigest()
        return SHA256Hash(value=hash_bytes)

    def __str__(self) -> str:
        return self.value
```

### 2.2 ToolCall

**File**: `domain/value_objects/tool_call.py`

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class ToolCall:
    """Immutable record of a tool invocation."""

    tool_name: str
    arguments: Dict[str, Any]
    result: Optional[str]
    error: Optional[str]
    duration_ms: int
    timestamp: datetime

    def is_success(self) -> bool:
        """Check if tool call succeeded."""
        return self.error is None

    def is_failure(self) -> bool:
        """Check if tool call failed."""
        return self.error is not None
```

---

## 3. Enums

**File**: `domain/entities/enums.py`

```python
from enum import Enum


class SessionState(str, Enum):
    """Agent session states."""

    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


class UIComponentType(str, Enum):
    """UI component types."""

    MARKDOWN = "markdown"
    CARD = "card"
    FORM = "form"
    PROGRESS = "progress"
    ACTION = "action"
    CONFIRMATION = "confirmation"
    VOICE = "voice"


class UIComponentState(str, Enum):
    """UI component lifecycle states."""

    CREATING = "creating"
    CREATED = "created"
    UPDATING = "updating"
    DISMISSED = "dismissed"


class ConsolidationTrigger(str, Enum):
    """Memory consolidation triggers."""

    SCHEDULED = "scheduled"  # Every 10 interactions
    MANUAL = "manual"  # User requested
    PRE_QUERY = "pre_query"  # Before query processing


class ConsolidationStatus(str, Enum):
    """Memory consolidation status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentStatus(str, Enum):
    """Agent processing status."""

    IDLE = "idle"
    THINKING = "thinking"
    USING_TOOL = "using_tool"
    COMPLETED = "completed"
    FAILED = "failed"


class VisibilityState(str, Enum):
    """Chat UI visibility state."""

    CHAT_VISIBLE = "chat_visible"
    CHAT_MINIMIZED = "chat_minimized"
    CHAT_HIDDEN = "chat_hidden"
```

---

## 4. Repository Interfaces

### 4.1 AgentSessionRepository

**File**: `domain/repositories/agent_session_repository.py`

```python
from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Optional

from domain.entities.agent_session import AgentSessionEntity


class AgentSessionRepository(ABC):
    """Repository for AgentSession entities.

    Implementations: RedisSessionAdapter, SQLiteSessionAdapter
    """

    @abstractmethod
    async def get_by_id(self, session_id: UUID) -> Optional[AgentSessionEntity]:
        """Retrieve session by ID."""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[AgentSessionEntity]:
        """Retrieve all sessions for a user."""
        pass

    @abstractmethod
    async def get_active_sessions(self, user_id: str) -> List[AgentSessionEntity]:
        """Retrieve active sessions for a user."""
        pass

    @abstractmethod
    async def create(self, session: AgentSessionEntity) -> AgentSessionEntity:
        """Create a new session."""
        pass

    @abstractmethod
    async def update(self, session: AgentSessionEntity) -> AgentSessionEntity:
        """Update an existing session."""
        pass

    @abstractmethod
    async def delete(self, session_id: UUID) -> bool:
        """Delete a session by ID."""
        pass

    @abstractmethod
    async def exists(self, session_id: UUID) -> bool:
        """Check if session exists."""
        pass
```

### 4.2 UIComponentRepository

**File**: `domain/repositories/ui_component_repository.py`

```python
from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Optional

from domain.entities.ui_component import UIComponentEntity


class UIComponentRepository(ABC):
    """Repository for UIComponent entities.

    Implementation: In-memory (session-scoped)
    """

    @abstractmethod
    async def get_by_id(self, component_id: UUID) -> Optional[UIComponentEntity]:
        """Retrieve component by ID."""
        pass

    @abstractmethod
    async def get_by_session_id(self, session_id: UUID) -> List[UIComponentEntity]:
        """Retrieve all components for a session."""
        pass

    @abstractmethod
    async def get_visible_components(self, session_id: UUID) -> List[UIComponentEntity]:
        """Retrieve visible components for a session."""
        pass

    @abstractmethod
    async def create(self, component: UIComponentEntity) -> UIComponentEntity:
        """Create a new component."""
        pass

    @abstractmethod
    async def update(self, component: UIComponentEntity) -> UIComponentEntity:
        """Update an existing component."""
        pass

    @abstractmethod
    async def dismiss(self, component_id: UUID) -> bool:
        """Dismiss a component by ID."""
        pass

    @abstractmethod
    async def dismiss_by_session(self, session_id: UUID) -> int:
        """Dismiss all components for a session. Returns count dismissed."""
        pass

    @abstractmethod
    async def delete(self, component_id: UUID) -> bool:
        """Delete a component by ID."""
        pass
```

### 4.3 MemoryRepository

**File**: `domain/repositories/memory_repository.py`

```python
from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Optional, Dict, Any

from domain.entities.memory_consolidation import MemoryConsolidationEntity


class MemoryRepository(ABC):
    """Repository for memory operations.

    Implementations: QdrantVectorStoreAdapter, Mem0MemoryAdapter
    """

    @abstractmethod
    async def store_memory(
        self,
        content: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UUID:
        """Store a memory. Returns memory ID."""
        pass

    @abstractmethod
    async def search_memories(
        self,
        query: str,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search memories by semantic similarity."""
        pass

    @abstractmethod
    async def get_all_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve all memories for a user."""
        pass

    @abstractmethod
    async def update_memory(self, memory_id: UUID, new_content: str) -> bool:
        """Update a memory by ID."""
        pass

    @abstractmethod
    async def delete_memory(self, memory_id: UUID) -> bool:
        """Delete a memory by ID."""
        pass

    @abstractmethod
    async def consolidate_memories(
        self,
        session_id: UUID,
        user_id: str
    ) -> MemoryConsolidationEntity:
        """Consolidate session memories to long-term storage."""
        pass
```

---

## 5. Domain Services

### 5.1 ValidationService

**File**: `domain/services/validation.py`

```python
from typing import List, Optional
from uuid import UUID

from domain.entities.agent_session import AgentSessionEntity
from domain.value_objects.sha256_hash import SHA256Hash


class ValidationService:
    """Domain service for business validation."""

    @staticmethod
    def validate_user_id(user_id: str) -> SHA256Hash:
        """Validate and return SHA-256 hash."""
        try:
            return SHA256Hash(value=user_id)
        except ValueError as e:
            raise ValueError(f"Invalid user_id: {e}")

    @staticmethod
    def validate_session_state_transition(
        current_state: str,
        new_state: str
    ) -> bool:
        """Validate session state transition is allowed."""
        allowed_transitions = {
            "initializing": ["active"],
            "active": ["paused", "closed"],
            "paused": ["active", "closed"],
            "closed": [],  # Terminal state
        }
        return new_state in allowed_transitions.get(current_state, [])

    @staticmethod
    def validate_reasoning_step_limit(current_step: int, max_step: int) -> bool:
        """Validate reasoning hasn't exceeded max iterations."""
        return current_step < max_step

    @staticmethod
    def validate_confidence_threshold(confidence: float, threshold: float) -> bool:
        """Validate confidence meets threshold."""
        return confidence >= threshold
```

---

## 6. Invariants

### Session Invariants

1. **Session ID is immutable**: Once created, `session_id` never changes
2. **User ID is immutable**: `user_id` hash never changes
3. **State transitions are controlled**: Only specific transitions allowed
4. **Closed sessions cannot be modified**: Once closed, state is frozen
5. **Activity timestamp always updates**: `last_activity_at` on every operation

### UI Component Invariants

1. **Component ID is immutable**: `component_id` never changes
2. **Type cannot change**: `component_type` is immutable
3. **Dismissed is terminal**: Once dismissed, cannot be updated
4. **Descriptor type must match component type**: Validation on update
5. **Dismissible is controlled**: Not all components can be dismissed

### Memory Invariants

1. **Memory ID is immutable**: UUID assigned once
2. **Consolidation is idempotent**: Multiple consolidations safe
3. **TTL is enforced**: Expired memories auto-deleted
4. **User isolation**: Memories never cross user boundaries

---

**This domain model is part of AGENTX LLD v1.0. All names and types are locked.**

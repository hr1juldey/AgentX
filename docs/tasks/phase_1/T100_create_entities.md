# T100: Create Domain Entities

**Phase**: 1
**Estimated Time**: 40 minutes
**Dependencies**: T001
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/domain_model.md` - Entity definitions
- `lld/incremental_release_plan.md` - Phase 1: All entities implemented

**Description**:
Creates all domain entity classes using dataclass pattern from Clean Architecture. These are the core business objects with no external dependencies.

---

## Acceptance Criteria

**Passing Criteria**:
- All 6 entity files exist in domain/entities/
- All entities use @dataclass pattern
- All entities have business methods
- All entities import successfully
- Entity state enums defined

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify entity files exist
test -f agentx/domain/entities/agent_session.py && echo "AgentSessionEntity exists"
test -f agentx/domain/entities/ui_component.py && echo "UIComponentEntity exists"
test -f agentx/domain/entities/memory_consolidation.py && echo "MemoryConsolidationEntity exists"
test -f agentx/domain/entities/conversation_turn.py && echo "ConversationTurnEntity exists"
test -f agentx/domain/entities/memory.py && echo "MemoryEntity exists"
test -f agentx/domain/entities/user.py && echo "UserEntity exists"

# Verify imports work
python3 -c "from agentx.domain.entities.agent_session import AgentSessionEntity; print('AgentSessionEntity OK')"
python3 -c "from agentx.domain.entities.ui_component import UIComponentEntity; print('UIComponentEntity OK')"
```

---

## Implementation Steps

### Step 1: Create enums for entity states

Create file `agentx/domain/entities/enums.py`:

```python
"""Enumeration types for domain entities."""

from enum import Enum


class SessionState(str, Enum):
    """Agent session states."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


class UIComponentType(str, Enum):
    """UI component types."""
    MARKDOWN_BLOCK = "markdown_block"
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
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    PRE_QUERY = "pre_query"


class ConsolidationStatus(str, Enum):
    """Memory consolidation status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
```

### Step 2: Create AgentSessionEntity

Create file `agentx/domain/entities/agent_session.py`:

```python
"""AgentSession entity representing a user session with the agent."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4
from typing import Dict, Any

from agentx.domain.entities.enums import SessionState


@dataclass
class AgentSessionEntity:
    """Represents a session between a user and the AI agent."""

    session_id: UUID
    user_id: str  # SHA-256 hash
    state: SessionState
    created_at: datetime
    modified_at: datetime
    last_activity_at: datetime
    metadata: Dict[str, Any]

    @classmethod
    def create(cls, user_id: str) -> "AgentSessionEntity":
        """Create a new session with defaults."""
        now = datetime.utcnow()
        return cls(
            session_id=uuid4(),
            user_id=user_id,
            state=SessionState.INITIALIZING,
            created_at=now,
            modified_at=now,
            last_activity_at=now,
            metadata={}
        )

    def is_active(self) -> bool:
        """Check if session is in active state."""
        return self.state == SessionState.ACTIVE

    def pause(self) -> None:
        """Transition session to paused state."""
        if self.state != SessionState.ACTIVE:
            raise ValueError(f"Cannot pause session in state: {self.state}")
        self.state = SessionState.PAUSED
        self._update_timestamp()

    def resume(self) -> None:
        """Transition session from paused to active."""
        if self.state != SessionState.PAUSED:
            raise ValueError(f"Cannot resume session in state: {self.state}")
        self.state = SessionState.ACTIVE
        self._update_timestamp()

    def close(self) -> None:
        """Transition session to closed state."""
        if self.state == SessionState.CLOSED:
            return
        self.state = SessionState.CLOSED
        self._update_timestamp()

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity_at = datetime.utcnow()

    def _update_timestamp(self) -> None:
        """Update modified timestamp."""
        self.modified_at = datetime.utcnow()
```

### Step 3: Create UIComponentEntity

Create file `agentx/domain/entities/ui_component.py`:

```python
"""UIComponent entity representing generative UI elements."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4
from typing import Dict, Any, Optional

from agentx.domain.entities.enums import UIComponentType, UIComponentState


@dataclass
class UIComponentEntity:
    """Represents a UI component generated by the agent."""

    component_id: UUID
    session_id: UUID
    component_type: UIComponentType
    state: UIComponentState
    descriptor: Dict[str, Any]  # UIDescriptor as dict
    created_at: datetime
    dismissed_at: Optional[datetime]
    metadata: Dict[str, Any]

    @classmethod
    def create(
        cls,
        session_id: UUID,
        component_type: UIComponentType,
        descriptor: Dict[str, Any]
    ) -> "UIComponentEntity":
        """Create a new UI component."""
        return cls(
            component_id=uuid4(),
            session_id=session_id,
            component_type=component_type,
            state=UIComponentState.CREATING,
            descriptor=descriptor,
            created_at=datetime.utcnow(),
            dismissed_at=None,
            metadata={}
        )

    def mark_created(self) -> None:
        """Transition component to created state."""
        if self.state != UIComponentState.CREATING:
            raise ValueError(f"Cannot mark created in state: {self.state}")
        self.state = UIComponentState.CREATED

    def update_descriptor(self, new_descriptor: Dict[str, Any]) -> None:
        """Update component descriptor."""
        if self.state == UIComponentState.DISMISSED:
            raise ValueError("Cannot update dismissed component")
        self.descriptor = new_descriptor
        self.state = UIComponentState.UPDATING

    def dismiss(self) -> None:
        """Dismiss the component."""
        if self.state == UIComponentState.DISMISSED:
            return
        self.state = UIComponentState.DISMISSED
        self.dismissed_at = datetime.utcnow()

    def is_dismissible(self) -> bool:
        """Check if component can be dismissed."""
        return self.state not in [UIComponentState.CREATING, UIComponentState.DISMISSED]

    def is_visible(self) -> bool:
        """Check if component should be visible."""
        return self.state in [UIComponentState.CREATED, UIComponentState.UPDATING]
```

### Step 4: Create MemoryConsolidationEntity

Create file `agentx/domain/entities/memory_consolidation.py`:

```python
"""MemoryConsolidation entity for memory consolidation operations."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from agentx.domain.entities.enums import ConsolidationTrigger, ConsolidationStatus


@dataclass
class MemoryConsolidationEntity:
    """Represents a memory consolidation operation."""

    consolidation_id: UUID
    session_id: UUID
    trigger: ConsolidationTrigger
    status: ConsolidationStatus
    started_at: datetime
    completed_at: datetime
    memories_processed: int
    memories_merged: int
    memories_invalidated: int
    error_message: str

    @classmethod
    def create(
        cls,
        session_id: UUID,
        trigger: ConsolidationTrigger
    ) -> "MemoryConsolidationEntity":
        """Create a new consolidation operation."""
        return cls(
            consolidation_id=uuid4(),
            session_id=session_id,
            trigger=trigger,
            status=ConsolidationStatus.PENDING,
            started_at=datetime.utcnow(),
            completed_at=datetime.min,
            memories_processed=0,
            memories_merged=0,
            memories_invalidated=0,
            error_message=""
        )

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

    def is_complete(self) -> bool:
        """Check if consolidation is complete (success or failure)."""
        return self.status in [
            ConsolidationStatus.COMPLETED,
            ConsolidationStatus.FAILED
        ]
```

### Step 5: Create ConversationTurnEntity

Create file `agentx/domain/entities/conversation_turn.py`:

```python
"""ConversationTurn entity for individual conversation messages."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, Dict, Any


class MessageRole(str):
    """Role of a message sender."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ConversationTurnEntity:
    """Represents a single turn in a conversation."""

    turn_id: UUID
    session_id: UUID
    role: str
    content: str
    timestamp: datetime
    tool_calls: Optional[list[Dict[str, Any]]]
    metadata: Dict[str, Any]

    @classmethod
    def create(
        cls,
        session_id: UUID,
        role: str,
        content: str
    ) -> "ConversationTurnEntity":
        """Create a new conversation turn."""
        return cls(
            turn_id=uuid4(),
            session_id=session_id,
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
            tool_calls=None,
            metadata={}
        )

    def is_from_user(self) -> bool:
        """Check if message is from user."""
        return self.role == MessageRole.USER

    def is_from_assistant(self) -> bool:
        """Check if message is from assistant."""
        return self.role == MessageRole.ASSISTANT
```

### Step 6: Create MemoryEntity

Create file `agentx/domain/entities/memory.py`:

```python
"""Memory entity for stored memories."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4
from typing import Dict, Any, Optional


class MemoryType(str):
    """Type of memory storage."""
    EPISODIC = "episodic"  # Specific events
    SEMANTIC = "semantic"  # General knowledge
    PROCEDURAL = "procedural"  # Skills and tasks


@dataclass
class MemoryEntity:
    """Represents a stored memory."""

    memory_id: UUID
    user_id: str  # SHA-256 hash
    content: str
    memory_type: str
    embedding: Optional[list[float]]  # Vector embedding
    metadata: Dict[str, Any]
    created_at: datetime
    last_accessed_at: datetime
    ttl_seconds: Optional[int]
    is_valid: bool

    @classmethod
    def create(
        cls,
        user_id: str,
        content: str,
        memory_type: str = MemoryType.EPISODIC,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "MemoryEntity":
        """Create a new memory."""
        now = datetime.utcnow()
        return cls(
            memory_id=uuid4(),
            user_id=user_id,
            content=content,
            memory_type=memory_type,
            embedding=None,
            metadata=metadata or {},
            created_at=now,
            last_accessed_at=now,
            ttl_seconds=None,
            is_valid=True
        )

    def access(self) -> None:
        """Update last accessed timestamp."""
        self.last_accessed_at = datetime.utcnow()

    def invalidate(self) -> None:
        """Mark memory as invalid."""
        self.is_valid = False

    def is_expired(self) -> bool:
        """Check if memory has expired based on TTL."""
        if self.ttl_seconds is None:
            return False
        expiry_time = self.created_at.timestamp() + self.ttl_seconds
        return datetime.utcnow().timestamp() > expiry_time

    def set_embedding(self, embedding: list[float]) -> None:
        """Set vector embedding for the memory."""
        self.embedding = embedding
```

### Step 7: Create UserEntity

Create file `agentx/domain/entities/user.py`:

```python
"""User entity for user management."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class UserEntity:
    """Represents a user (SHA-256 hashed ID)."""

    user_id: str  # SHA-256 hash
    created_at: datetime
    last_seen_at: datetime
    preferences: Dict[str, Any]
    metadata: Dict[str, Any]

    @classmethod
    def create(cls, raw_user_id: str) -> "UserEntity":
        """Create a new user with hashed ID."""
        import hashlib
        hashed_id = hashlib.sha256(raw_user_id.encode()).hexdigest()
        now = datetime.utcnow()
        return cls(
            user_id=hashed_id,
            created_at=now,
            last_seen_at=now,
            metadata={},
            preferences={}
        )

    def update_last_seen(self) -> None:
        """Update last seen timestamp."""
        self.last_seen_at = datetime.utcnow()

    def set_preference(self, key: str, value: Any) -> None:
        """Set a user preference."""
        self.preferences[key] = value

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference."""
        return self.preferences.get(key, default)
```

### Step 8: Update entities/__init__.py

Update file `agentx/domain/entities/__init__.py`:

```python
"""Domain entity classes."""

from agentx.domain.entities.enums import (
    SessionState,
    UIComponentType,
    UIComponentState,
    ConsolidationTrigger,
    ConsolidationStatus,
)
from agentx.domain.entities.agent_session import AgentSessionEntity
from agentx.domain.entities.ui_component import UIComponentEntity
from agentx.domain.entities.memory_consolidation import MemoryConsolidationEntity
from agentx.domain.entities.conversation_turn import ConversationTurnEntity, MessageRole
from agentx.domain.entities.memory import MemoryEntity, MemoryType
from agentx.domain.entities.user import UserEntity

__all__ = [
    "SessionState",
    "UIComponentType",
    "UIComponentState",
    "ConsolidationTrigger",
    "ConsolidationStatus",
    "AgentSessionEntity",
    "UIComponentEntity",
    "MemoryConsolidationEntity",
    "ConversationTurnEntity",
    "MessageRole",
    "MemoryEntity",
    "MemoryType",
    "UserEntity",
]
```

---

## Expected Failures & Countermeasures

### Failure: Circular import errors

**Likelihood**: Low
**Symptoms**: `ImportError: cannot import name 'SessionState'`

**Countermeasures**:
1. Ensure enums.py is created before entities that import it
2. Use absolute imports only (no relative imports)
3. Check import order in __init__.py

**Recovery Time**: 2 minutes

### Failure: Datetime import issues

**Likelihood**: Low
**Symptoms**: `NameError: name 'datetime' is not defined`

**Countermeasures**:
1. Ensure `from datetime import datetime` at top of each file
2. Use `datetime.utcnow()` not `datetime.now()`

**Recovery Time**: 1 minute

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T001 directory structure changed
**Detection**: agentx/domain/entities/ directory missing
**Action**: Re-run T001 to ensure all directories exist

**Recovery Time**: 5 minutes

### Downstream Impact

**Scenario**: Entity field names change
**Prevention**: All entity field names are LOCKED
**Mitigation**: If changes absolutely required, update all downstream DTOs, mappers, repositories
**Affected Tasks**: T101-T199 (all Phase 1 tasks)

---

## Artifacts

**Files Created**:
- `agentx/domain/entities/enums.py` (Enums, LOCKED)
- `agentx/domain/entities/agent_session.py` (Entity, LOCKED)
- `agentx/domain/entities/ui_component.py` (Entity, LOCKED)
- `agentx/domain/entities/memory_consolidation.py` (Entity, LOCKED)
- `agentx/domain/entities/conversation_turn.py` (Entity, LOCKED)
- `agentx/domain/entities/memory.py` (Entity, LOCKED)
- `agentx/domain/entities/user.py` (Entity, LOCKED)
- `agentx/domain/entities/__init__.py` (Exports, not locked)

**Locked APIs**:
- All entity class names
- All entity field names and types
- All entity business method signatures
- All enum values

---

## Quality Gates

**Quality Checks**:
- **Check**: All entity files exist
  - Command: `ls agentx/domain/entities/*.py`
  - Expected: 8 .py files (7 entities + __init__.py)
  - Required: Yes

- **Check**: All entities can be imported
  - Command: `python3 -c "from agentx.domain.entities import AgentSessionEntity, UIComponentEntity, MemoryEntity; print('All entities OK')"`
  - Expected: `All entities OK`
  - Required: Yes

- **Check**: Entity factory methods work
  - Command: `python3 -c "from agentx.domain.entities import AgentSessionEntity; s = AgentSessionEntity.create('test_hash'); print(s.state)"`
  - Expected: `SessionState.INITIALIZING`
  - Required: Yes

---

## Notes

1. All entities use @dataclass pattern (Clean Architecture)
2. All entities have factory methods (create())
3. All entities have business logic methods (state transitions)
4. No external dependencies (only datetime, uuid, typing)
5. All field names and types are LOCKED

---

## Completion Checklist

- [ ] enums.py created with all enums
- [ ] AgentSessionEntity created with business methods
- [ ] UIComponentEntity created with lifecycle methods
- [ ] MemoryConsolidationEntity created with status tracking
- [ ] ConversationTurnEntity created with role helpers
- [ ] MemoryEntity created with embedding and TTL support
- [ ] UserEntity created with hash ID and preferences
- [ ] entities/__init__.py exports all entities
- [ ] All import tests pass
- [ ] Ready for T101 (Repository Implementations)

---

**Task T100 is part of Phase 1: Domain + Infrastructure**
**Locked APIs**: All entity class names, field names, method signatures

# T008: Create Stub Repositories

**Phase**: 0
**Estimated Time**: 30 minutes
**Dependencies**: T001
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/domain_model.md` - Repository interfaces
- `lld/incremental_release_plan.md` - Phase 0: All repositories stubbed

**Description**:
Creates stub implementations of all repository interfaces. These raise NotImplementedError and serve as placeholders for Phase 1 when real implementations are added.

---

## Acceptance Criteria

**Passing Criteria**:
- All repository interface files exist in domain/repositories/
- Stub implementations exist in infrastructure/ (optional for Phase 0)
- Stubs raise NotImplementedError with descriptive messages
- Import structure is correct (will fail at runtime, that's OK)

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify interface files exist
test -f agentx/domain/repositories/agent_session_repository.py && echo "AgentSessionRepository exists"
test -f agentx/domain/repositories/ui_component_repository.py && echo "UIComponentRepository exists"
test -f agentx/domain/repositories/memory_repository.py && echo "MemoryRepository exists"

# Verify interfaces can be imported (will fail on implementations, that's OK)
python3 -c "from domain.repositories.agent_session_repository import AgentSessionRepository; print('Interface import OK')"
```

---

## Implementation Steps

### Step 1: Create AgentSessionRepository interface

Create file `agentx/domain/repositories/agent_session_repository.py`:

```python
"""Repository interface for AgentSession entities."""

from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Optional

from domain.entities.agent_session import AgentSessionEntity


class AgentSessionRepository(ABC):
    """Repository for AgentSession entities.

    Implementations: RedisSessionAdapter, SQLiteSessionAdapter (Phase 1)
    """

    @abstractmethod
    async def get_by_id(self, session_id: UUID) -> Optional[AgentSessionEntity]:
        """Retrieve session by ID.

        Args:
            session_id: Unique session identifier

        Returns:
            AgentSessionEntity if found, None otherwise
        """
        raise NotImplementedError("Phase 1: Use RedisSessionAdapter or SQLiteSessionAdapter")

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[AgentSessionEntity]:
        """Retrieve all sessions for a user.

        Args:
            user_id: SHA-256 hash of user ID

        Returns:
            List of AgentSessionEntity
        """
        raise NotImplementedError("Phase 1: Use RedisSessionAdapter or SQLiteSessionAdapter")

    @abstractmethod
    async def get_active_sessions(self, user_id: str) -> List[AgentSessionEntity]:
        """Retrieve active sessions for a user.

        Args:
            user_id: SHA-256 hash of user ID

        Returns:
            List of active AgentSessionEntity
        """
        raise NotImplementedError("Phase 1: Use RedisSessionAdapter or SQLiteSessionAdapter")

    @abstractmethod
    async def create(self, session: AgentSessionEntity) -> AgentSessionEntity:
        """Create a new session.

        Args:
            session: AgentSessionEntity to create

        Returns:
            Created AgentSessionEntity
        """
        raise NotImplementedError("Phase 1: Use RedisSessionAdapter or SQLiteSessionAdapter")

    @abstractmethod
    async def update(self, session: AgentSessionEntity) -> AgentSessionEntity:
        """Update an existing session.

        Args:
            session: AgentSessionEntity with updates

        Returns:
            Updated AgentSessionEntity
        """
        raise NotImplementedError("Phase 1: Use RedisSessionAdapter or SQLiteSessionAdapter")

    @abstractmethod
    async def delete(self, session_id: UUID) -> bool:
        """Delete a session by ID.

        Args:
            session_id: Unique session identifier

        Returns:
            True if deleted, False otherwise
        """
        raise NotImplementedError("Phase 1: Use RedisSessionAdapter or SQLiteSessionAdapter")

    @abstractmethod
    async def exists(self, session_id: UUID) -> bool:
        """Check if session exists.

        Args:
            session_id: Unique session identifier

        Returns:
            True if exists, False otherwise
        """
        raise NotImplementedError("Phase 1: Use RedisSessionAdapter or SQLiteSessionAdapter")
```

### Step 2: Create UIComponentRepository interface

Create file `agentx/domain/repositories/ui_component_repository.py`:

```python
"""Repository interface for UIComponent entities."""

from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Optional

from domain.entities.ui_component import UIComponentEntity


class UIComponentRepository(ABC):
    """Repository for UIComponent entities.

    Implementation: In-memory (session-scoped) - Phase 3
    """

    @abstractmethod
    async def get_by_id(self, component_id: UUID) -> Optional[UIComponentEntity]:
        """Retrieve component by ID.

        Args:
            component_id: Unique component identifier

        Returns:
            UIComponentEntity if found, None otherwise
        """
        raise NotImplementedError("Phase 3: UI component repository")

    @abstractmethod
    async def get_by_session_id(self, session_id: UUID) -> List[UIComponentEntity]:
        """Retrieve all components for a session.

        Args:
            session_id: Session identifier

        Returns:
            List of UIComponentEntity
        """
        raise NotImplementedError("Phase 3: UI component repository")

    @abstractmethod
    async def get_visible_components(self, session_id: UUID) -> List[UIComponentEntity]:
        """Retrieve visible components for a session.

        Args:
            session_id: Session identifier

        Returns:
            List of visible UIComponentEntity
        """
        raise NotImplementedError("Phase 3: UI component repository")

    @abstractmethod
    async def create(self, component: UIComponentEntity) -> UIComponentEntity:
        """Create a new component.

        Args:
            component: UIComponentEntity to create

        Returns:
            Created UIComponentEntity
        """
        raise NotImplementedError("Phase 3: UI component repository")

    @abstractmethod
    async def update(self, component: UIComponentEntity) -> UIComponentEntity:
        """Update an existing component.

        Args:
            component: UIComponentEntity with updates

        Returns:
            Updated UIComponentEntity
        """
        raise NotImplementedError("Phase 3: UI component repository")

    @abstractmethod
    async def dismiss(self, component_id: UUID) -> bool:
        """Dismiss a component by ID.

        Args:
            component_id: Unique component identifier

        Returns:
            True if dismissed, False otherwise
        """
        raise NotImplementedError("Phase 3: UI component repository")

    @abstractmethod
    async def dismiss_by_session(self, session_id: UUID) -> int:
        """Dismiss all components for a session.

        Args:
            session_id: Session identifier

        Returns:
            Number of components dismissed
        """
        raise NotImplementedError("Phase 3: UI component repository")

    @abstractmethod
    async def delete(self, component_id: UUID) -> bool:
        """Delete a component by ID.

        Args:
            component_id: Unique component identifier

        Returns:
            True if deleted, False otherwise
        """
        raise NotImplementedError("Phase 3: UI component repository")
```

### Step 3: Create MemoryRepository interface

Create file `agentx/domain/repositories/memory_repository.py`:

```python
"""Repository interface for memory operations."""

from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Dict, Any, Optional

from domain.entities.memory_consolidation import MemoryConsolidationEntity


class MemoryRepository(ABC):
    """Repository for memory operations.

    Implementations: QdrantVectorStoreAdapter, Mem0MemoryAdapter (Phase 1/5)
    """

    @abstractmethod
    async def store_memory(
        self,
        content: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UUID:
        """Store a memory.

        Args:
            content: Memory content to store
            user_id: SHA-256 hash of user ID
            metadata: Optional metadata

        Returns:
            Memory ID (UUID)
        """
        raise NotImplementedError("Phase 1: Use QdrantVectorStoreAdapter")

    @abstractmethod
    async def search_memories(
        self,
        query: str,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search memories by semantic similarity.

        Args:
            query: Search query
            user_id: SHA-256 hash of user ID
            limit: Maximum results

        Returns:
            List of memory results
        """
        raise NotImplementedError("Phase 1: Use QdrantVectorStoreAdapter")

    @abstractmethod
    async def get_all_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve all memories for a user.

        Args:
            user_id: SHA-256 hash of user ID

        Returns:
            List of all memories
        """
        raise NotImplementedError("Phase 1: Use QdrantVectorStoreAdapter")

    @abstractmethod
    async def update_memory(self, memory_id: UUID, new_content: str) -> bool:
        """Update a memory by ID.

        Args:
            memory_id: Memory ID
            new_content: New content

        Returns:
            True if updated, False otherwise
        """
        raise NotImplementedError("Phase 1: Use QdrantVectorStoreAdapter")

    @abstractmethod
    async def delete_memory(self, memory_id: UUID) -> bool:
        """Delete a memory by ID.

        Args:
            memory_id: Memory ID

        Returns:
            True if deleted, False otherwise
        """
        raise NotImplementedError("Phase 1: Use QdrantVectorStoreAdapter")

    @abstractmethod
    async def consolidate_memories(
        self,
        session_id: UUID,
        user_id: str
    ) -> MemoryConsolidationEntity:
        """Consolidate session memories to long-term storage.

        Args:
            session_id: Session identifier
            user_id: SHA-256 hash of user ID

        Returns:
            MemoryConsolidationEntity with results
        """
        raise NotImplementedError("Phase 5: Memory consolidation")
```

### Step 4: Update domain/repositories/__init__.py

Create file `agentx/domain/repositories/__init__.py`:

```python
"""Domain repository interfaces."""

from agentx.domain.repositories.agent_session_repository import AgentSessionRepository
from agentx.domain.repositories.ui_component_repository import UIComponentRepository
from agentx.domain.repositories.memory_repository import MemoryRepository

__all__ = [
    "AgentSessionRepository",
    "UIComponentRepository",
    "MemoryRepository",
]
```

---

## Expected Failures & Countermeasures

### Failure: Entity imports fail

**Likelihood**: High (entities not created yet)
**Symptoms**: `ModuleNotFoundError: No module named 'domain.entities.agent_session'`

**Countermeasures**:
1. This is EXPECTED in Phase 0 - entities created in Phase 1
2. Interface file structure is correct
3. Imports will work when Phase 1 adds entities

**Recovery Time**: 0 minutes (expected failure)

### Failure: ABC import fails

**Likelihood**: Low
**Symptoms**: `ModuleNotFoundError: No module named 'abc'`

**Countermeasures**:
1. abc is built-in module, should always be available
2. Check Python version: `python3 --version`

**Recovery Time**: 1 minute

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T001 directory structure changed
**Detection**: domain/repositories/ directory missing
**Action**: Re-run T001 to ensure all directories exist

**Recovery Time**: 5 minutes

### Downstream Impact

**Scenario**: Repository interface methods change
**Prevention**: All method signatures are LOCKED
**Mitigation**: If changes absolutely required, update Phase 1 implementations
**Affected Tasks**: All Phase 1+ tasks using repositories

---

## Artifacts

**Files Created**:
- `agentx/domain/repositories/agent_session_repository.py` (Interface, LOCKED)
- `agentx/domain/repositories/ui_component_repository.py` (Interface, LOCKED)
- `agentx/domain/repositories/memory_repository.py` (Interface, LOCKED)
- `agentx/domain/repositories/__init__.py` (Package marker, not locked)

**Locked APIs**:
- All repository class names
- All repository method signatures (names, parameters, return types)
- NotImplementedError messages indicate which phase implements them

---

## Quality Gates

**Quality Checks**:
- **Check**: Interface files exist
  - Command: `ls agentx/domain/repositories/*.py`
  - Expected: At least 4 .py files (3 interfaces + __init__.py)
  - Required: Yes

- **Check**: Can import interfaces (will fail on entities, OK in Phase 0)
  - Command: `python3 -c "from domain.repositories.agent_session_repository import AgentSessionRepository; print('Interface OK')"` 2>&1 | head -1
  - Expected: `Interface OK` (or import error for entities, which is OK)
  - Required: For interface structure only

---

## Notes

1. Repository interfaces are LOCKED - method signatures cannot change
2. All methods raise NotImplementedError (Phase 0 pattern)
3. Phase 1 will create concrete implementations
4. Entities imported will fail in Phase 0 (created in Phase 1)
5. This is expected - structure is correct even if imports fail

---

## Completion Checklist

- [ ] AgentSessionRepository interface created
- [ ] UIComponentRepository interface created
- [ ] MemoryRepository interface created
- [ ] All methods have NotImplementedError
- [ ] All method signatures match LLD
- [ ] repositories/__init__.py exports all interfaces
- [ ] Ready for T009 (Basic Configuration)

---

**Task T008 is part of Phase 0: Minimal System**
**Locked APIs**: All repository interface method signatures

# T502: Create Memory Consolidation

**Phase**: 5
**Estimated Time**: 45 minutes
**Dependencies**: T001, T100, T500
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/domain_model.md` - Memory consolidation entity
- `lld/infrastructure_adapters.md` - Consolidation service
- `lld/incremental_release_plan.md` - Phase 5: Memory consolidation

**Description**:
Creates memory consolidation service that periodically summarizes and merges memories. Implements scheduled and manual consolidation triggers.

---

## Acceptance Criteria

**Passing Criteria**:
- application/services/memory_consolidation.py exists
- Implements consolidate_session() method
- Implements schedule_consolidation() method
- Updates memory repository
- Can be imported

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify file exists
test -f agentx/application/services/memory_consolidation.py && echo "Consolidation service exists"

# Verify import works
python3 -c "from agentx.application.services.memory_consolidation import MemoryConsolidationService; print('Import OK')"
```

---

## Implementation Steps

### Step 1: Create memory consolidation service

Create file `agentx/application/services/memory_consolidation.py`:

```python
"""Memory consolidation service."""

import asyncio
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta

from agentx.domain.entities.memory_consolidation import (
    MemoryConsolidationEntity,
    ConsolidationTrigger,
    ConsolidationStatus,
)
from agentx.domain.repositories.memory_repository import MemoryRepository
from agentx.core.dependencies import get_memory_repository


class MemoryConsolidationService:
    """Service for consolidating memories.

    This service periodically summarizes and merges memories to prevent
    memory bloat and improve retrieval quality.

    Example:
        >>> service = MemoryConsolidationService()
        >>> result = await service.consolidate_session(session_id, user_id)
    """

    def __init__(
        self,
        memory_repository: MemoryRepository = None,
        consolidation_interval: int = 10  # interactions
    ):
        """Initialize consolidation service.

        Args:
            memory_repository: Memory repository instance
            consolidation_interval: Interactions between consolidations
        """
        self.memory_repository = memory_repository or get_memory_repository()
        self.consolidation_interval = consolidation_interval

        # Track session interaction counts
        self.session_counters: Dict[str, int] = {}

    async def consolidate_session(
        self,
        session_id: UUID,
        user_id: str,
        trigger: ConsolidationTrigger = ConsolidationTrigger.MANUAL
    ) -> MemoryConsolidationEntity:
        """Consolidate memories for a session.

        Args:
            session_id: Session to consolidate
            user_id: User identifier (SHA-256 hash)
            trigger: What triggered consolidation

        Returns:
            Consolidation result entity
        """
        consolidation = MemoryConsolidationEntity.create(
            session_id=session_id,
            trigger=trigger
        )
        consolidation.start()

        try:
            # Phase 5: Basic consolidation
            # Phase 7: Full summarization with LLM

            # Get all memories for user
            all_memories = await self.memory_repository.get_all_memories(user_id)

            # Filter memories for this session (if tracked)
            session_memories = self._filter_session_memories(
                all_memories,
                session_id
            )

            # Phase 5: Count and clean up
            # Phase 7: Summarize and merge
            processed = len(session_memories)
            merged = 0
            invalidated = 0

            consolidation.complete(
                processed=processed,
                merged=merged,
                invalidated=invalidated
            )

            # Reset counter for this session
            if str(session_id) in self.session_counters:
                del self.session_counters[str(session_id)]

        except Exception as e:
            consolidation.fail(str(e))

        return consolidation

    def _filter_session_memories(
        self,
        all_memories: List[Dict[str, Any]],
        session_id: UUID
    ) -> List[Dict[str, Any]]:
        """Filter memories for specific session.

        Args:
            all_memories: All user memories
            session_id: Session identifier

        Returns:
            Memories for this session
        """
        # Phase 5: Simple filtering
        # Phase 7: Use session metadata in memory payload
        session_str = str(session_id)

        filtered = []
        for memory in all_memories:
            # Check if memory belongs to session
            metadata = memory.get("metadata", {})
            if metadata.get("session_id") == session_str:
                filtered.append(memory)

        return filtered

    async def check_consolidation_needed(
        self,
        session_id: UUID
    ) -> bool:
        """Check if session needs consolidation.

        Args:
            session_id: Session identifier

        Returns:
            True if consolidation needed
        """
        session_str = str(session_id)
        count = self.session_counters.get(session_str, 0)

        return count >= self.consolidation_interval

    async def record_interaction(self, session_id: UUID) -> None:
        """Record an interaction for consolidation tracking.

        Args:
            session_id: Session identifier
        """
        session_str = str(session_id)
        self.session_counters[session_str] = self.session_counters.get(session_str, 0) + 1

        # Check if consolidation should trigger
        if await self.check_consolidation_needed(session_id):
            # Trigger scheduled consolidation in background
            asyncio.create_task(self._trigger_scheduled_consolidation(session_id))

    async def _trigger_scheduled_consolidation(self, session_id: UUID) -> None:
        """Trigger scheduled consolidation in background.

        Args:
            session_id: Session identifier
        """
        # Get user_id from session (would need session repository)
        # For Phase 5, use placeholder
        user_id = "placeholder_user_hash"

        await self.consolidate_session(
            session_id=session_id,
            user_id=user_id,
            trigger=ConsolidationTrigger.SCHEDULED
        )

    async def get_consolidation_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[MemoryConsolidationEntity]:
        """Get consolidation history for user.

        Args:
            user_id: User identifier
            limit: Maximum results

        Returns:
            List of past consolidations

        Note:
            Phase 5: Returns empty list (not tracking history yet)
            Phase 7: Implement full history tracking
        """
        # Phase 5: Not implemented
        # Phase 7: Return from database
        return []


def get_memory_consolidation_service() -> MemoryConsolidationService:
    """Get memory consolidation service instance.

    Returns:
        MemoryConsolidationService instance
    """
    return MemoryConsolidationService()
```

### Step 2: Create application services __init__.py

Create file `agentx/application/services/__init__.py`:

```python
"""Application services."""

from agentx.application.services.memory_consolidation import (
    MemoryConsolidationService,
    get_memory_consolidation_service,
)

__all__ = [
    "MemoryConsolidationService",
    "get_memory_consolidation_service",
]
```

---

## Expected Failures & Countermeasures

### Failure: Memory repository not available

**Likelihood**: Low
**Symptoms**: `AttributeError: 'NoneType' object has no attribute 'get_all_memories'`

**Countermeasures**:
1. Ensure T500 (Memory Repository) is complete
2. Check dependencies.py returns valid repository
3. Fallback to empty list if repository unavailable

**Recovery Time**: 5 minutes

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T500 memory repository changed
**Detection**: Repository method signatures changed
**Action**: Update service to use new repository interface

**Recovery Time**: 10 minutes

### Downstream Impact

**Scenario**: Service class name changes
**Prevention**: Class name is LOCKED
**Mitigation**: Update all use sites
**Affected Tasks**: T503 (Tests)

---

## Artifacts

**Files Created**:
- `agentx/application/services/memory_consolidation.py` (Consolidation service, LOCKED)
- `agentx/application/services/__init__.py` (Package marker)

**Locked APIs**:
- MemoryConsolidationService class name
- All method signatures
- get_memory_consolidation_service() function signature

---

## Quality Gates

**Quality Checks**:
- **Check**: Service file exists
  - Command: `test -f agentx/application/services/memory_consolidation.py && echo "OK"`
  - Expected: `OK`
  - Required: Yes

- **Check**: Can be imported
  - Command: `python3 -c "from agentx.application.services.memory_consolidation import MemoryConsolidationService; print('OK')"`
  - Expected: `OK`
  - Required: Yes

---

## Notes

1. Consolidation interval: every 10 interactions (configurable)
2. Triggers: MANUAL (user), SCHEDULED (automatic), PRE_QUERY (before query)
3. Phase 5: Basic counting and cleanup
4. Phase 7: Full LLM-based summarization
5. Background consolidation doesn't block queries
6. Session counters tracked in memory

---

## Completion Checklist

- [ ] memory_consolidation.py created
- [ ] MemoryConsolidationService class defined
- [ ] consolidate_session() method implemented
- [ ] check_consolidation_needed() method implemented
- [ ] record_interaction() method implemented
- [ ] services/__init__.py created
- [ ] get_memory_consolidation_service() factory function
- [ ] All imports work
- [ ] Ready for T503 (Phase 5 Tests)

---

**Task T502 is part of Phase 5: Memory + RAG**
**Locked APIs**: Service class name, method signatures

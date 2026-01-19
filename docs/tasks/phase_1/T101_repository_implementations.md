# T101: Create Repository Implementations

**Phase**: 1
**Estimated Time**: 50 minutes
**Dependencies**: T001, T008, T100
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/infrastructure_adapters.md` - Repository adapters
- `lld/domain_model.md` - Repository interfaces (from T008)
- `lld/incremental_release_plan.md` - Phase 1: Qdrant, Redis, SQLite adapters

**Description**:
Creates concrete implementations of all repository interfaces. This includes Qdrant vector store, Redis session storage, and SQLite long-term storage.

---

## Acceptance Criteria

**Passing Criteria**:
- QdrantVectorStoreAdapter implements MemoryRepository
- RedisSessionAdapter implements AgentSessionRepository
- SQLiteSessionAdapter implements AgentSessionRepository
- InMemoryUIComponentRepository implements UIComponentRepository
- All adapters can be imported
- No NotImplementedError raised (Phase 1 has real implementations)

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify adapter files exist
test -f agentx/infrastructure/external/qdrant_vector_store.py && echo "Qdrant adapter exists"
test -f agentx/infrastructure/external/redis_session_adapter.py && echo "Redis adapter exists"
test -f agentx/infrastructure/external/sqlite_session_adapter.py && echo "SQLite adapter exists"
test -f agentx/infrastructure/external/in_memory_ui_repository.py && echo "In-memory UI repo exists"

# Verify imports work
python3 -c "from agentx.infrastructure.external.qdrant_vector_store import QdrantVectorStoreAdapter; print('Qdrant OK')"
python3 -c "from agentx.infrastructure.external.redis_session_adapter import RedisSessionAdapter; print('Redis OK')"
python3 -c "from agentx.infrastructure.external.sqlite_session_adapter import SQLiteSessionAdapter; print('SQLite OK')"
```

---

## Implementation Steps

### Step 1: Create QdrantVectorStoreAdapter

Create file `agentx/infrastructure/external/qdrant_vector_store.py`:

```python
"""Qdrant vector store adapter for memory operations."""

from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

from agentx.domain.entities.memory import MemoryEntity
from agentx.domain.entities.conversation_turn import ConversationTurnEntity
from agentx.domain.entities.memory_consolidation import MemoryConsolidationEntity
from agentx.domain.repositories.memory_repository import MemoryRepository


class QdrantVectorStoreAdapter(MemoryRepository):
    """Qdrant-based vector store implementation."""

    def __init__(
        self,
        client: AsyncQdrantClient,
        collection_name: str,
        embedding_dim: int = 384
    ):
        self.client = client
        self.collection_name = collection_name
        self.embedding_dim = embedding_dim

    async def _ensure_collection(self) -> None:
        """Ensure collection exists."""
        collections = await self.client.get_collections()
        collection_names = [c.name for c in collections.collections]
        if self.collection_name not in collection_names:
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE
                )
            )

    async def store_memory(
        self,
        content: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UUID:
        """Store a memory with vector embedding."""
        await self._ensure_collection()

        memory_id = uuid4()
        # TODO: Generate actual embedding with sentence-transformers
        embedding = [0.0] * self.embedding_dim

        point = PointStruct(
            id=str(memory_id),
            vector=embedding,
            payload={
                "content": content,
                "user_id": user_id,
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat()
            }
        )

        await self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

        return memory_id

    async def search_memories(
        self,
        query: str,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search memories by semantic similarity."""
        await self._ensure_collection()

        # TODO: Generate query embedding
        query_embedding = [0.0] * self.embedding_dim

        results = await self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=Filter(
                must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
            ),
            limit=limit
        )

        return [
            {
                "memory_id": UUID(hit.id),
                "content": hit.payload["content"],
                "score": hit.score,
                "metadata": hit.payload.get("metadata", {})
            }
            for hit in results
        ]

    async def get_all_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve all memories for a user."""
        await self._ensure_collection()

        results = await self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=Filter(
                must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
            ),
            limit=1000
        )

        return [
            {
                "memory_id": UUID(point.id),
                "content": point.payload["content"],
                "metadata": point.payload.get("metadata", {})
            }
            for point in results[0]
        ]

    async def update_memory(self, memory_id: UUID, new_content: str) -> bool:
        """Update a memory by ID."""
        await self._ensure_collection()

        # TODO: Generate new embedding
        new_embedding = [0.0] * self.embedding_dim

        await self.client.set_payload(
            collection_name=self.collection_name,
            payload={"content": new_content},
            points=[str(memory_id)]
        )

        # Update vector
        await self.client.upsert(
            collection_name=self.collection_name,
            points=[PointStruct(id=str(memory_id), vector=new_embedding, payload={})]
        )

        return True

    async def delete_memory(self, memory_id: UUID) -> bool:
        """Delete a memory by ID."""
        await self._ensure_collection()

        await self.client.delete(
            collection_name=self.collection_name,
            points_selector=[str(memory_id)]
        )

        return True

    async def consolidate_memories(
        self,
        session_id: UUID,
        user_id: str
    ) -> MemoryConsolidationEntity:
        """Consolidate session memories to long-term storage."""
        # This is a stub for Phase 1
        # Full implementation in Phase 5
        consolidation = MemoryConsolidationEntity.create(
            session_id=session_id,
            trigger=ConsolidationTrigger.MANUAL
        )
        consolidation.fail("Phase 5: Memory consolidation not implemented")
        return consolidation
```

### Step 2: Create RedisSessionAdapter

Create file `agentx/infrastructure/external/redis_session_adapter.py`:

```python
"""Redis session adapter for active session storage."""

from typing import List, Optional
from uuid import UUID
import json

from redis import Redis

from agentx.domain.entities.agent_session import AgentSessionEntity, SessionState
from agentx.domain.repositories.agent_session_repository import AgentSessionRepository


class RedisSessionAdapter(AgentSessionRepository):
    """Redis-based session storage for active sessions."""

    def __init__(self, redis_client: Redis, ttl_seconds: int = 3600):
        self.redis = redis_client
        self.ttl_seconds = ttl_seconds
        self.session_prefix = "session:"

    def _session_key(self, session_id: UUID) -> str:
        """Generate Redis key for session."""
        return f"{self.session_prefix}{session_id}"

    def _serialize_session(self, session: AgentSessionEntity) -> str:
        """Serialize session to JSON."""
        return json.dumps({
            "session_id": str(session.session_id),
            "user_id": session.user_id,
            "state": session.state.value,
            "created_at": session.created_at.isoformat(),
            "modified_at": session.modified_at.isoformat(),
            "last_activity_at": session.last_activity_at.isoformat(),
            "metadata": session.metadata
        })

    def _deserialize_session(self, data: str) -> AgentSessionEntity:
        """Deserialize JSON to session."""
        from datetime import datetime
        parsed = json.loads(data)
        return AgentSessionEntity(
            session_id=UUID(parsed["session_id"]),
            user_id=parsed["user_id"],
            state=SessionState(parsed["state"]),
            created_at=datetime.fromisoformat(parsed["created_at"]),
            modified_at=datetime.fromisoformat(parsed["modified_at"]),
            last_activity_at=datetime.fromisoformat(parsed["last_activity_at"]),
            metadata=parsed.get("metadata", {})
        )

    async def get_by_id(self, session_id: UUID) -> Optional[AgentSessionEntity]:
        """Retrieve session by ID."""
        key = self._session_key(session_id)
        data = self.redis.get(key)
        if not data:
            return None
        return self._deserialize_session(data)

    async def get_by_user_id(self, user_id: str) -> List[AgentSessionEntity]:
        """Retrieve all sessions for a user."""
        pattern = f"{self.session_prefix}*"
        keys = self.redis.keys(pattern)
        sessions = []
        for key in keys:
            data = self.redis.get(key)
            if data:
                session = self._deserialize_session(data)
                if session.user_id == user_id:
                    sessions.append(session)
        return sessions

    async def get_active_sessions(self, user_id: str) -> List[AgentSessionEntity]:
        """Retrieve active sessions for a user."""
        all_sessions = await self.get_by_user_id(user_id)
        return [s for s in all_sessions if s.state == SessionState.ACTIVE]

    async def create(self, session: AgentSessionEntity) -> AgentSessionEntity:
        """Create a new session."""
        key = self._session_key(session.session_id)
        data = self._serialize_session(session)
        self.redis.setex(key, self.ttl_seconds, data)
        return session

    async def update(self, session: AgentSessionEntity) -> AgentSessionEntity:
        """Update an existing session."""
        key = self._session_key(session.session_id)
        if not self.redis.exists(key):
            raise ValueError(f"Session {session.session_id} not found")
        data = self._serialize_session(session)
        self.redis.setex(key, self.ttl_seconds, data)
        return session

    async def delete(self, session_id: UUID) -> bool:
        """Delete a session by ID."""
        key = self._session_key(session_id)
        return bool(self.redis.delete(key))

    async def exists(self, session_id: UUID) -> bool:
        """Check if session exists."""
        key = self._session_key(session_id)
        return bool(self.redis.exists(key))
```

### Step 3: Create SQLiteSessionAdapter

Create file `agentx/infrastructure/external/sqlite_session_adapter.py`:

```python
"""SQLite session adapter for long-term session storage."""

from typing import List, Optional
from uuid import UUID
import sqlite3
import json
from datetime import datetime

from agentx.domain.entities.agent_session import AgentSessionEntity, SessionState
from agentx.domain.repositories.agent_session_repository import AgentSessionRepository


class SQLiteSessionAdapter(AgentSessionRepository):
    """SQLite-based session storage for persistence."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                state TEXT NOT NULL,
                created_at TEXT NOT NULL,
                modified_at TEXT NOT NULL,
                last_activity_at TEXT NOT NULL,
                metadata TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def _row_to_session(self, row: sqlite3.Row) -> AgentSessionEntity:
        """Convert database row to session entity."""
        return AgentSessionEntity(
            session_id=UUID(row["session_id"]),
            user_id=row["user_id"],
            state=SessionState(row["state"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            modified_at=datetime.fromisoformat(row["modified_at"]),
            last_activity_at=datetime.fromisoformat(row["last_activity_at"]),
            metadata=json.loads(row["metadata"])
        )

    async def get_by_id(self, session_id: UUID) -> Optional[AgentSessionEntity]:
        """Retrieve session by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM agent_sessions WHERE session_id = ?",
            (str(session_id),)
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return self._row_to_session(row)

    async def get_by_user_id(self, user_id: str) -> List[AgentSessionEntity]:
        """Retrieve all sessions for a user."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM agent_sessions WHERE user_id = ?",
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_session(row) for row in rows]

    async def get_active_sessions(self, user_id: str) -> List[AgentSessionEntity]:
        """Retrieve active sessions for a user."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM agent_sessions WHERE user_id = ? AND state = ?",
            (user_id, SessionState.ACTIVE.value)
        )
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_session(row) for row in rows]

    async def create(self, session: AgentSessionEntity) -> AgentSessionEntity:
        """Create a new session."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO agent_sessions
            (session_id, user_id, state, created_at, modified_at, last_activity_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            str(session.session_id),
            session.user_id,
            session.state.value,
            session.created_at.isoformat(),
            session.modified_at.isoformat(),
            session.last_activity_at.isoformat(),
            json.dumps(session.metadata)
        ))
        conn.commit()
        conn.close()
        return session

    async def update(self, session: AgentSessionEntity) -> AgentSessionEntity:
        """Update an existing session."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE agent_sessions
            SET user_id = ?, state = ?, modified_at = ?, last_activity_at = ?, metadata = ?
            WHERE session_id = ?
        """, (
            session.user_id,
            session.state.value,
            session.modified_at.isoformat(),
            session.last_activity_at.isoformat(),
            json.dumps(session.metadata),
            str(session.session_id)
        ))
        conn.commit()
        conn.close()
        return session

    async def delete(self, session_id: UUID) -> bool:
        """Delete a session by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM agent_sessions WHERE session_id = ?",
            (str(session_id),)
        )
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    async def exists(self, session_id: UUID) -> bool:
        """Check if session exists."""
        result = await self.get_by_id(session_id)
        return result is not None
```

### Step 4: Create InMemoryUIComponentRepository

Create file `agentx/infrastructure/external/in_memory_ui_repository.py`:

```python
"""In-memory UI component repository for session-scoped UI state."""

from typing import List, Dict, Optional
from uuid import UUID

from agentx.domain.entities.ui_component import UIComponentEntity, UIComponentState
from agentx.domain.repositories.ui_component_repository import UIComponentRepository


class InMemoryUIComponentRepository(UIComponentRepository):
    """In-memory repository for UI components (session-scoped)."""

    def __init__(self):
        self._components: Dict[UUID, UIComponentEntity] = {}

    async def get_by_id(self, component_id: UUID) -> Optional[UIComponentEntity]:
        """Retrieve component by ID."""
        return self._components.get(component_id)

    async def get_by_session_id(self, session_id: UUID) -> List[UIComponentEntity]:
        """Retrieve all components for a session."""
        return [
            comp for comp in self._components.values()
            if comp.session_id == session_id
        ]

    async def get_visible_components(self, session_id: UUID) -> List[UIComponentEntity]:
        """Retrieve visible components for a session."""
        session_components = await self.get_by_session_id(session_id)
        return [comp for comp in session_components if comp.is_visible()]

    async def create(self, component: UIComponentEntity) -> UIComponentEntity:
        """Create a new component."""
        self._components[component.component_id] = component
        return component

    async def update(self, component: UIComponentEntity) -> UIComponentEntity:
        """Update an existing component."""
        if component.component_id not in self._components:
            raise ValueError(f"Component {component.component_id} not found")
        self._components[component.component_id] = component
        return component

    async def dismiss(self, component_id: UUID) -> bool:
        """Dismiss a component by ID."""
        component = self._components.get(component_id)
        if not component:
            return False
        component.dismiss()
        return True

    async def dismiss_by_session(self, session_id: UUID) -> int:
        """Dismiss all components for a session."""
        count = 0
        for comp in await self.get_by_session_id(session_id):
            if comp.is_dismissible():
                comp.dismiss()
                count += 1
        return count

    async def delete(self, component_id: UUID) -> bool:
        """Delete a component by ID."""
        if component_id not in self._components:
            return False
        del self._components[component_id]
        return True
```

### Step 5: Update infrastructure/__init__.py

Update file `agentx/infrastructure/__init__.py`:

```python
"""Infrastructure adapters package."""
```

### Step 6: Update infrastructure/external/__init__.py

Update file `agentx/infrastructure/external/__init__.py`:

```python
"""External infrastructure adapters."""

from agentx.infrastructure.external.qdrant_vector_store import QdrantVectorStoreAdapter
from agentx.infrastructure.external.redis_session_adapter import RedisSessionAdapter
from agentx.infrastructure.external.sqlite_session_adapter import SQLiteSessionAdapter
from agentx.infrastructure.external.in_memory_ui_repository import InMemoryUIComponentRepository

__all__ = [
    "QdrantVectorStoreAdapter",
    "RedisSessionAdapter",
    "SQLiteSessionAdapter",
    "InMemoryUIComponentRepository",
]
```

---

## Expected Failures & Countermeasures

### Failure: qdrant-client not installed

**Likelihood**: Medium
**Symptoms**: `ModuleNotFoundError: No module named 'qdrant_client'`

**Countermeasures**:
1. Install qdrant-client: `uv pip install qdrant-client`
2. Or stub out Qdrant methods for Phase 0
3. Add qdrant-client to requirements.txt

**Recovery Time**: 3 minutes

### Failure: Redis connection refused

**Likelihood**: Medium
**Symptoms**: `redis.exceptions.ConnectionError: Error connecting to Redis`

**Countermeasures**:
1. Start Redis: `docker run -d -p 6379:6379 redis:alpine`
2. Or use system Redis: `sudo systemctl start redis`
3. Or fall back to SQLite adapter

**Recovery Time**: 5 minutes

### Failure: SQLite database permission error

**Likelihood**: Low
**Symptoms**: `sqlite3.OperationalError: unable to open database file`

**Countermeasures**:
1. Create data directory: `mkdir -p data`
2. Check permissions on data directory
3. Use absolute path for SQLite db

**Recovery Time**: 2 minutes

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T008 repository interfaces changed
**Detection**: NotImplementedError still raised, method signature mismatch
**Action**: Re-run T008 or update implementations to match new interface

**Recovery Time**: 10 minutes

**Scenario**: T100 entities changed
**Detection**: Entity field names don't match
**Action**: Re-run T100 or update serialization/deserialization

**Recovery Time**: 10 minutes

### Downstream Impact

**Scenario**: Adapter method names change
**Prevention**: All adapter method names are LOCKED by repository interfaces
**Mitigation**: Update dependency injection in T003
**Affected Tasks**: T102 (Ollama Adapter), T103 (Update DI)

---

## Artifacts

**Files Created**:
- `agentx/infrastructure/external/qdrant_vector_store.py` (Qdrant adapter, LOCKED)
- `agentx/infrastructure/external/redis_session_adapter.py` (Redis adapter, LOCKED)
- `agentx/infrastructure/external/sqlite_session_adapter.py` (SQLite adapter, LOCKED)
- `agentx/infrastructure/external/in_memory_ui_repository.py` (In-memory UI repo, LOCKED)

**Files Modified**:
- `agentx/infrastructure/__init__.py`
- `agentx/infrastructure/external/__init__.py`

**Locked APIs**:
- All adapter class names
- All adapter method signatures (inherited from repository interfaces)
- Serialization formats (JSON for Redis, SQLite schema)

---

## Quality Gates

**Quality Checks**:
- **Check**: All adapter files exist
  - Command: `ls agentx/infrastructure/external/*.py`
  - Expected: 4+ adapter files
  - Required: Yes

- **Check**: All adapters can be imported
  - Command: `python3 -c "from agentx.infrastructure.external import QdrantVectorStoreAdapter, RedisSessionAdapter, SQLiteSessionAdapter, InMemoryUIComponentRepository; print('All adapters OK')"`
  - Expected: `All adapters OK`
  - Required: Yes

---

## Notes

1. Qdrant adapter uses placeholder embeddings (0.0) - real embeddings in Phase 2
2. Redis adapter uses JSON serialization with TTL
3. SQLite adapter auto-initializes schema
4. In-memory UI repository is session-scoped (not persisted)
5. All adapters follow repository interfaces from T008

---

## Completion Checklist

- [ ] QdrantVectorStoreAdapter implements all MemoryRepository methods
- [ ] RedisSessionAdapter implements all AgentSessionRepository methods
- [ ] SQLiteSessionAdapter implements all AgentSessionRepository methods
- [ ] InMemoryUIComponentRepository implements all UIComponentRepository methods
- [ ] All adapters can be imported
- [ ] Ready for T102 (Ollama LLM Adapter)

---

**Task T101 is part of Phase 1: Domain + Infrastructure**
**Locked APIs**: All adapter implementations

# AGENTX Infrastructure Adapters LLD

**Version**: 1.0.0
**Date**: 2026-01-19
**Status**: Locked
**Dependencies**: domain_model.md

---

## Table of Contents

1. [Qdrant Adapter](#1-qdrant-adapter)
2. [Redis Session Adapter](#2-redis-session-adapter)
3. [SQLite Session Adapter](#3-sqlite-session-adapter)
4. [Ollama LLM Adapter](#4-ollama-llm-adapter)
5. [Mem0 Memory Adapter](#5-mem0-memory-adapter)
6. [WebSocket Manager](#6-websocket-manager)

---

## 1. Qdrant Adapter

### 1.1 QdrantVectorStoreAdapter

**File**: `infrastructure/external/qdrant_vector_store.py`

```python
from uuid import UUID
from typing import List, Dict, Any, Optional
from datetime import datetime

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter

from domain.repositories.memory_repository import MemoryRepository


class QdrantVectorStoreAdapter(MemoryRepository):
    """Qdrant vector database adapter for semantic memory storage.

    Three-tier memory architecture:
    - Tier 1: DSPy History (short-term, conversation context)
    - Tier 2: Agent's private collection (mid-term, per-session)
    - Tier 3: User's main collection (long-term, persistent)
    """

    def __init__(
        self,
        client: AsyncQdrantClient,
        collection_name: str = "agentx_memories",
        embedding_dim: int = 384
    ):
        self._client = client
        self._collection_name = collection_name
        self._embedding_dim = embedding_dim

    async def _ensure_collection(self) -> None:
        """Ensure collection exists."""
        collections = await self._client.get_collections()
        if not any(c.name == self._collection_name for c in collections.collections):
            await self._client.create_collection(
                collection_name=self._collection_name,
                vectors_config=VectorParams(
                    size=self._embedding_dim,
                    distance=Distance.COSINE
                )
            )

    async def _embed_text(self, text: str) -> List[float]:
        """Generate embedding for text (uses Ollama nomic-embed-text)."""
        # Import here to avoid circular dependency
        from infrastructure.external.ollama_llm import OllamaLLMAdapter
        ollama = OllamaLLMAdapter(base_url="http://localhost:11434")
        return await ollama.embed(text)

    async def store_memory(
        self,
        content: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UUID:
        """Store a memory with vector embedding."""
        await self._ensure_collection()

        memory_id = UUID(bytes=UUID(user_id.encode()).bytes)  # Generate UUID
        embedding = await self._embed_text(content)

        point = PointStruct(
            id=str(memory_id),
            vector=embedding,
            payload={
                "content": content,
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                **(metadata or {})
            }
        )

        await self._client.upsert(
            collection_name=self._collection_name,
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

        query_embedding = await self._embed_text(query)

        results = await self._client.search(
            collection_name=self._collection_name,
            query_vector=query_embedding,
            query_filter=Filter(must=[{"key": "user_id", "match": {"value": user_id}}]),
            limit=limit
        )

        return [
            {
                "memory_id": UUID(hit.id),
                "content": hit.payload.get("content"),
                "score": hit.score,
                "metadata": {k: v for k, v in hit.payload.items() if k not in ["content", "user_id"]}
            }
            for hit in results
        ]

    async def get_all_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve all memories for a user."""
        await self._ensure_collection()

        results = await self._client.scroll(
            collection_name=self._collection_name,
            scroll_filter=Filter(must=[{"key": "user_id", "match": {"value": user_id}}]),
            limit=1000
        )

        return [
            {
                "memory_id": UUID(point.id),
                "content": point.payload.get("content"),
                "metadata": {k: v for k, v in point.payload.items() if k != "content"}
            }
            for point in results[0]
        ]

    async def update_memory(self, memory_id: UUID, new_content: str) -> bool:
        """Update a memory by ID."""
        await self._ensure_collection()

        new_embedding = await self._embed_text(new_content)

        await self._client.set_payload(
            collection_name=self._collection_name,
            payload={"content": new_content},
            points=[str(memory_id)]
        )

        # Update vector by recreating point
        existing = await self._client.retrieve(
            collection_name=self._collection_name,
            ids=[str(memory_id)]
        )

        if existing:
            await self._client.upsert(
                collection_name=self._collection_name,
                points=[PointStruct(
                    id=str(memory_id),
                    vector=new_embedding,
                    payload={
                        **existing[0].payload,
                        "content": new_content,
                        "updated_at": datetime.utcnow().isoformat()
                    }
                )]
            )
            return True

        return False

    async def delete_memory(self, memory_id: UUID) -> bool:
        """Delete a memory by ID."""
        await self._ensure_collection()

        await self._client.delete(
            collection_name=self._collection_name,
            points_selector=[str(memory_id)]
        )
        return True

    async def consolidate_memories(
        self,
        session_id: UUID,
        user_id: str
    ) -> MemoryConsolidationEntity:
        """Consolidate session memories to long-term storage."""
        # This would involve Tier 2 -> Tier 3 promotion
        # Implementation depends on consolidation strategy
        pass
```

---

## 2. Redis Session Adapter

### 2.1 RedisSessionAdapter

**File**: `infrastructure/database/redis_session_adapter.py`

```python
import json
from uuid import UUID
from typing import List, Optional
from datetime import datetime, timedelta

from redis import Redis

from domain.repositories.agent_session_repository import AgentSessionRepository
from domain.entities.agent_session import AgentSessionEntity
from domain.entities.enums import SessionState


class RedisSessionAdapter(AgentSessionRepository):
    """Redis adapter for active session storage (fast, TTL-based)."""

    def __init__(
        self,
        redis_client: Redis,
        ttl_seconds: int = 3600,
        key_prefix: str = "agentx:session"
    ):
        self._redis = redis_client
        self._ttl = ttl_seconds
        self._key_prefix = key_prefix

    def _make_key(self, session_id: UUID) -> str:
        """Generate Redis key for session."""
        return f"{self._key_prefix}:{session_id}"

    def _serialize(self, session: AgentSessionEntity) -> str:
        """Serialize session to JSON."""
        return json.dumps({
            "session_id": str(session.session_id),
            "user_id": session.user_id,
            "state": session.state.value,
            "created_at": session.created_at.isoformat(),
            "modified_at": session.modified_at.isoformat(),
            "last_activity_at": session.last_activity_at.isoformat(),
            "current_reasoning_step": session.current_reasoning_step,
            "total_tool_calls": session.total_tool_calls,
        })

    def _deserialize(self, data: str) -> AgentSessionEntity:
        """Deserialize JSON to session."""
        obj = json.loads(data)
        return AgentSessionEntity(
            session_id=UUID(obj["session_id"]),
            user_id=obj["user_id"],
            state=SessionState(obj["state"]),
            created_at=datetime.fromisoformat(obj["created_at"]),
            modified_at=datetime.fromisoformat(obj["modified_at"]),
            last_activity_at=datetime.fromisoformat(obj["last_activity_at"]),
            current_reasoning_step=obj.get("current_reasoning_step", 0),
            total_tool_calls=obj.get("total_tool_calls", 0),
        )

    async def get_by_id(self, session_id: UUID) -> Optional[AgentSessionEntity]:
        """Retrieve session by ID."""
        key = self._make_key(session_id)
        data = self._redis.get(key)
        if not data:
            return None
        return self._deserialize(data)

    async def get_by_user_id(self, user_id: str) -> List[AgentSessionEntity]:
        """Retrieve all sessions for a user."""
        pattern = f"{self._key_prefix}:*"
        sessions = []

        for key in self._redis.scan_iter(match=pattern):
            data = self._redis.get(key)
            if data:
                session = self._deserialize(data)
                if session.user_id == user_id:
                    sessions.append(session)

        return sessions

    async def get_active_sessions(self, user_id: str) -> List[AgentSessionEntity]:
        """Retrieve active sessions for a user."""
        all_sessions = await self.get_by_user_id(user_id)
        return [s for s in all_sessions if s.is_active()]

    async def create(self, session: AgentSessionEntity) -> AgentSessionEntity:
        """Create a new session."""
        key = self._make_key(session.session_id)
        data = self._serialize(session)

        self._redis.setex(
            name=key,
            time=self._ttl,
            value=data
        )

        return session

    async def update(self, session: AgentSessionEntity) -> AgentSessionEntity:
        """Update an existing session."""
        key = self._make_key(session.session_id)

        if not self._redis.exists(key):
            raise ValueError(f"Session not found: {session.session_id}")

        data = self._serialize(session)
        self._redis.setex(key, self._ttl, data)

        return session

    async def delete(self, session_id: UUID) -> bool:
        """Delete a session by ID."""
        key = self._make_key(session_id)
        return bool(self._redis.delete(key))

    async def exists(self, session_id: UUID) -> bool:
        """Check if session exists."""
        key = self._make_key(session_id)
        return bool(self._redis.exists(key))
```

---

## 3. SQLite Session Adapter

### 3.1 SQLiteSessionAdapter

**File**: `infrastructure/database/sqlite_session_adapter.py`

```python
import sqlite3
import json
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from domain.repositories.agent_session_repository import AgentSessionRepository
from domain.entities.agent_session import AgentSessionEntity
from domain.entities.enums import SessionState


class SQLiteSessionAdapter(AgentSessionRepository):
    """SQLite adapter for long-term session persistence."""

    def __init__(self, db_path: str = "data/sessions.db"):
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    state TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    modified_at TEXT NOT NULL,
                    last_activity_at TEXT NOT NULL,
                    current_reasoning_step INTEGER DEFAULT 0,
                    total_tool_calls INTEGER DEFAULT 0,
                    INDEX (user_id),
                    INDEX (state),
                    INDEX (last_activity_at)
                )
            """)

    async def get_by_id(self, session_id: UUID) -> Optional[AgentSessionEntity]:
        """Retrieve session by ID."""
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM agent_sessions WHERE session_id = ?",
                (str(session_id),)
            )
            row = cursor.fetchone()

            if not row:
                return None

            return self._row_to_entity(row)

    async def get_by_user_id(self, user_id: str) -> List[AgentSessionEntity]:
        """Retrieve all sessions for a user."""
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM agent_sessions WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            )

            return [self._row_to_entity(row) for row in cursor.fetchall()]

    async def get_active_sessions(self, user_id: str) -> List[AgentSessionEntity]:
        """Retrieve active sessions for a user."""
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM agent_sessions WHERE user_id = ? AND state = ? ORDER BY created_at DESC",
                (user_id, SessionState.ACTIVE.value)
            )

            return [self._row_to_entity(row) for row in cursor.fetchall()]

    async def create(self, session: AgentSessionEntity) -> AgentSessionEntity:
        """Create a new session."""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                INSERT INTO agent_sessions (
                    session_id, user_id, state, created_at, modified_at,
                    last_activity_at, current_reasoning_step, total_tool_calls
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(session.session_id),
                session.user_id,
                session.state.value,
                session.created_at.isoformat(),
                session.modified_at.isoformat(),
                session.last_activity_at.isoformat(),
                session.current_reasoning_step,
                session.total_tool_calls,
            ))

        return session

    async def update(self, session: AgentSessionEntity) -> AgentSessionEntity:
        """Update an existing session."""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute("""
                UPDATE agent_sessions SET
                    state = ?, modified_at = ?, last_activity_at = ?,
                    current_reasoning_step = ?, total_tool_calls = ?
                WHERE session_id = ?
            """, (
                session.state.value,
                session.modified_at.isoformat(),
                session.last_activity_at.isoformat(),
                session.current_reasoning_step,
                session.total_tool_calls,
                str(session.session_id),
            ))

            if cursor.rowcount == 0:
                raise ValueError(f"Session not found: {session.session_id}")

        return session

    async def delete(self, session_id: UUID) -> bool:
        """Delete a session by ID."""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM agent_sessions WHERE session_id = ?",
                (str(session_id),)
            )
            return cursor.rowcount > 0

    async def exists(self, session_id: UUID) -> bool:
        """Check if session exists."""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM agent_sessions WHERE session_id = ?",
                (str(session_id),)
            )
            return cursor.fetchone() is not None

    @staticmethod
    def _row_to_entity(row: sqlite3.Row) -> AgentSessionEntity:
        """Convert database row to entity."""
        return AgentSessionEntity(
            session_id=UUID(row["session_id"]),
            user_id=row["user_id"],
            state=SessionState(row["state"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            modified_at=datetime.fromisoformat(row["modified_at"]),
            last_activity_at=datetime.fromisoformat(row["last_activity_at"]),
            current_reasoning_step=row["current_reasoning_step"],
            total_tool_calls=row["total_tool_calls"],
        )
```

---

## 4. Ollama LLM Adapter

### 4.1 OllamaLLMAdapter

**File**: `infrastructure/external/ollama_llm.py`

```python
from typing import List, Dict, Any, AsyncIterator
import aiohttp
import dspy


class OllamaLLMAdapter:
    """Ollama LLM adapter for DSPy integration.

    Supports models: gemma3:4b, llama3.2, llava, qwen2.5-coder
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "gemma3:4b",
        timeout_seconds: int = 120
    ):
        self._base_url = base_url
        self._model = model
        self._timeout = timeout_seconds

    def get_dspy_lm(self) -> dspy.LM:
        """Get DSPy LM instance configured for Ollama."""
        return dspy.LM(
            f"ollama_chat/{self._model}",
            api_base=self._base_url,
            api_key="",  # Ollama doesn't require API key
        )

    async def generate_response(
        self,
        prompt: str,
        context: List[Dict[str, str]]
    ) -> str:
        """Generate a response from the LLM."""
        messages = [{"role": "user", "content": prompt}]
        messages.extend(context)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self._base_url}/api/chat",
                json={
                    "model": self._model,
                    "messages": messages,
                    "stream": False
                },
                timeout=aiohttp.ClientTimeout(total=self._timeout)
            ) as response:
                result = await response.json()
                return result.get("message", {}).get("content", "")

    async def stream_response(
        self,
        prompt: str,
        context: List[Dict[str, str]]
    ) -> AsyncIterator[str]:
        """Stream response from the LLM."""
        messages = [{"role": "user", "content": prompt}]
        messages.extend(context)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self._base_url}/api/chat",
                json={
                    "model": self._model,
                    "messages": messages,
                    "stream": True
                },
                timeout=aiohttp.ClientTimeout(total=self._timeout)
            ) as response:
                async for line in response.content:
                    if line:
                        chunk = line.decode()
                        if chunk.startswith("data: "):
                            data = chunk[6:]
                            import json
                            try:
                                parsed = json.loads(data)
                                content = parsed.get("message", {}).get("content", "")
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                pass

    async def embed(self, text: str) -> List[float]:
        """Generate embedding for text (using nomic-embed-text)."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self._base_url}/api/embeddings",
                json={
                    "model": "nomic-embed-text",
                    "prompt": text
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                result = await response.json()
                return result.get("embedding", [])

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the configured model."""
        return {
            "model": self._model,
            "base_url": self._base_url,
            "timeout_seconds": self._timeout,
        }
```

---

## 5. Mem0 Memory Adapter

### 5.1 Mem0MemoryAdapter

**File**: `infrastructure/external/mem0_memory.py`

```python
from uuid import UUID
from typing import List, Dict, Any, Optional

from mem0 import Memory

from domain.repositories.memory_repository import MemoryRepository


class Mem0MemoryAdapter(MemoryRepository):
    """Mem0AI adapter for long-term memory with consolidation.

    Handles Tier 3 (long-term) memory storage.
    """

    def __init__(self, memory: Memory):
        self._memory = memory

    async def store_memory(
        self,
        content: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UUID:
        """Store a memory in Mem0AI."""
        result = self._memory.add(
            content,
            user_id=user_id,
            metadata=metadata or {}
        )

        # Mem0 returns result with 'id' field
        memory_id = result.get("id", UUID(bytes=user_id.encode()))
        return UUID(str(memory_id))

    async def search_memories(
        self,
        query: str,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search memories in Mem0AI."""
        results = self._memory.search(
            query=query,
            user_id=user_id,
            limit=limit
        )

        return [
            {
                "memory_id": UUID(str(r.get("id", UUID(bytes=user_id.encode())))),
                "content": r.get("memory"),
                "metadata": r.get("metadata", {}),
                "score": r.get("score", 0.0)
            }
            for r in results.get("results", [])
        ]

    async def get_all_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve all memories for a user."""
        results = self._memory.get_all(user_id=user_id)

        return [
            {
                "memory_id": UUID(str(r.get("id"))),
                "content": r.get("memory"),
                "metadata": r.get("metadata", {})
            }
            for r in results.get("results", [])
        ]

    async def update_memory(self, memory_id: UUID, new_content: str) -> bool:
        """Update a memory in Mem0AI."""
        self._memory.update(memory_id=str(memory_id), data=new_content)
        return True

    async def delete_memory(self, memory_id: UUID) -> bool:
        """Delete a memory from Mem0AI."""
        self._memory.delete(memory_id=str(memory_id))
        return True

    async def consolidate_memories(
        self,
        session_id: UUID,
        user_id: str
    ) -> MemoryConsolidationEntity:
        """Consolidate memories with Mem0AI's built-in consolidation."""
        # Mem0 has automatic consolidation
        # This would trigger explicit consolidation if needed
        pass
```

---

## 6. WebSocket Manager

### 6.1 WebSocketManager

**File**: `infrastructure/external/websocket_manager.py`

```python
from typing import Dict, Set, Any
from fastapi import WebSocket
from uuid import UUID
import json
import asyncio

from ui.protocols.websocket_messages import WebSocketMessage, WebSocketMessageType


class WebSocketManager:
    """Manages WebSocket connections for streaming UI updates."""

    def __init__(self):
        self._connections: Dict[UUID, WebSocket] = {}
        self._queues: Dict[UUID, asyncio.Queue] = {}

    async def connect(self, session_id: UUID, websocket: WebSocket) -> None:
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        self._connections[session_id] = websocket
        self._queues[session_id] = asyncio.Queue()

    def disconnect(self, session_id: UUID) -> None:
        """Remove a WebSocket connection."""
        self._connections.pop(session_id, None)
        self._queues.pop(session_id, None)

    async def send_message(
        self,
        session_id: UUID,
        message_type: WebSocketMessageType,
        data: Dict[str, Any]
    ) -> None:
        """Send a message to a specific session."""
        websocket = self._connections.get(session_id)
        if not websocket:
            return

        message = WebSocketMessage(
            message_type=message_type,
            session_id=str(session_id),
            data=data
        )

        await websocket.send_json(message.model_dump())

    async def broadcast(
        self,
        message_type: WebSocketMessageType,
        data: Dict[str, Any]
    ) -> None:
        """Broadcast a message to all connected sessions."""
        for session_id in self._connections:
            await self.send_message(session_id, message_type, data)

    async def stream_tokens(
        self,
        session_id: UUID,
        token_generator: Any
    ) -> None:
        """Stream tokens to a session."""
        async for token in token_generator:
            await self.send_message(
                session_id,
                WebSocketMessageType.TOKEN,
                {"token": token}
            )

    async def send_ui_descriptor(
        self,
        session_id: UUID,
        descriptor: Dict[str, Any],
        action: str = "create"
    ) -> None:
        """Send a UI descriptor update."""
        if action == "create":
            message_type = WebSocketMessageType.DESCRIPTOR_CREATE
        elif action == "update":
            message_type = WebSocketMessageType.DESCRIPTOR_UPDATE
        elif action == "dismiss":
            message_type = WebSocketMessageType.DESCRIPTOR_DISMISS
        else:
            raise ValueError(f"Invalid UI action: {action}")

        await self.send_message(
            session_id,
            message_type,
            {"descriptor": descriptor}
        )

    def get_queue(self, session_id: UUID) -> asyncio.Queue:
        """Get the message queue for a session."""
        return self._queues.get(session_id, asyncio.Queue())

    async def process_queue(self, session_id: UUID) -> None:
        """Process messages from the queue (background task)."""
        queue = self.get_queue(session_id)

        while True:
            message = await queue.get()
            await self.send_message(
                session_id,
                message["type"],
                message["data"]
            )
```

---

**This infrastructure adapters document is part of AGENTX LLD v1.0. All names and types are locked.**

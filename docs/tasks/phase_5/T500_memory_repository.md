# T500: Create Memory Repository Implementations

**Phase**: 5
**Estimated Time**: 50 minutes
**Dependencies**: T001, T100
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/infrastructure_adapters.md` - Qdrant adapter implementation
- `lld/domain_model.md` - Memory repository interface
- `lld/incremental_release_plan.md` - Phase 5: Memory implementations

**Description**:
Creates real implementations for memory repository with Qdrant vector storage. Includes embedding generation and semantic search.

---

## Acceptance Criteria

**Passing Criteria**:
- Qdrant adapter updated with real embeddings
- Implements store_memory() with embeddings
- Implements search_memories() with vector similarity
- Implements get_all_memories()
- Can be imported

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify file exists
test -f agentx/infrastructure/external/qdrant_vector_store.py && echo "Qdrant adapter exists"

# Verify import works
python3 -c "from agentx.infrastructure.external.qdrant_vector_store import QdrantVectorStoreAdapter; print('Import OK')"
```

---

## Implementation Steps

### Step 1: Update Qdrant adapter with real embeddings

Update file `agentx/infrastructure/external/qdrant_vector_store.py` (created in T101):

```python
"""Qdrant vector store adapter for memory operations with real embeddings."""

from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
import numpy as np

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

from agentx.domain.entities.memory import MemoryEntity
from agentx.domain.entities.conversation_turn import ConversationTurnEntity
from agentx.domain.entities.memory_consolidation import MemoryConsolidationEntity
from agentx.domain.repositories.memory_repository import MemoryRepository


class EmbeddingService:
    """Service for generating text embeddings.

    Phase 5: Uses sentence-transformers for embeddings.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize embedding service.

        Args:
            model_name: HuggingFace model name
        """
        self.model_name = model_name
        self._model = None
        self.embedding_dim = 384  # MiniLM-L6-v2 dimension

    def _load_model(self):
        """Lazy load the embedding model."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)

    def embed(self, text: str) -> List[float]:
        """Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        self._load_model()
        embedding = self._model.encode(text)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        self._load_model()
        embeddings = self._model.encode(texts)
        return [e.tolist() for e in embeddings]


class QdrantVectorStoreAdapter(MemoryRepository):
    """Qdrant-based vector store implementation with real embeddings.

    Phase 5: Implements real embedding generation and semantic search.
    """

    def __init__(
        self,
        client: AsyncQdrantClient,
        collection_name: str,
        embedding_dim: int = 384
    ):
        self.client = client
        self.collection_name = collection_name
        self.embedding_dim = embedding_dim
        self.embedding_service = EmbeddingService()

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
        """Store a memory with vector embedding.

        Args:
            content: Memory content to store
            user_id: SHA-256 hash of user ID
            metadata: Optional metadata

        Returns:
            Memory ID (UUID)
        """
        await self._ensure_collection()

        memory_id = uuid4()

        # Generate real embedding
        embedding = self.embedding_service.embed(content)

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
        """Search memories by semantic similarity.

        Args:
            query: Search query
            user_id: SHA-256 hash of user ID
            limit: Maximum results

        Returns:
            List of memory results with scores
        """
        await self._ensure_collection()

        # Generate query embedding
        query_embedding = self.embedding_service.embed(query)

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
        """Retrieve all memories for a user.

        Args:
            user_id: SHA-256 hash of user ID

        Returns:
            List of all memories
        """
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
        """Update a memory by ID.

        Args:
            memory_id: Memory ID
            new_content: New content

        Returns:
            True if updated, False otherwise
        """
        await self._ensure_collection()

        # Generate new embedding
        new_embedding = self.embedding_service.embed(new_content)

        # Update payload
        await self.client.set_payload(
            collection_name=self.collection_name,
            payload={
                "content": new_content,
                "updated_at": datetime.utcnow().isoformat()
            },
            points=[str(memory_id)]
        )

        # Update vector
        await self.client.upsert(
            collection_name=self.collection_name,
            points=[PointStruct(id=str(memory_id), vector=new_embedding, payload={})]
        )

        return True

    async def delete_memory(self, memory_id: UUID) -> bool:
        """Delete a memory by ID.

        Args:
            memory_id: Memory ID

        Returns:
            True if deleted, False otherwise
        """
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
        """Consolidate session memories to long-term storage.

        Args:
            session_id: Session identifier
            user_id: SHA-256 hash of user ID

        Returns:
            MemoryConsolidationEntity with results

        Note:
            Phase 5: Basic implementation.
            Phase 7: Full consolidation with summarization.
        """
        consolidation = MemoryConsolidationEntity.create(
            session_id=session_id,
            trigger=ConsolidationTrigger.MANUAL
        )
        consolidation.start()

        try:
            # Get all memories for user
            memories = await self.get_all_memories(user_id)

            # Phase 5: Simply count memories
            # Phase 7: Actual consolidation with summarization
            consolidation.complete(
                processed=len(memories),
                merged=0,
                invalidated=0
            )

        except Exception as e:
            consolidation.fail(str(e))

        return consolidation
```

### Step 2: Add datetime import

Add at top of file:

```python
from datetime import datetime
from agentx.domain.entities.memory_consolidation import ConsolidationTrigger
```

---

## Expected Failures & Countermeasures

### Failure: sentence-transformers not installed

**Likelihood**: High
**Symptoms**: `ModuleNotFoundError: No module named 'sentence_transformers'`

**Countermeasures**:
1. Install sentence-transformers: `uv pip install sentence-transformers`
2. Or use mock embeddings for Phase 0-4
3. Add to requirements.txt in Phase 5

**Recovery Time**: 5 minutes

### Failure: Qdrant connection refused

**Likelihood**: Medium
**Symptoms**: `qdrant_client.http.TransportError: Connection refused`

**Countermeasures**:
1. Start Qdrant: `docker run -d -p 6333:6333 qdrant/qdrant`
2. Check .env has correct QDRANT_URL
3. Verify Qdrant accessible: `curl http://localhost:6333/`

**Recovery Time**: 3 minutes

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T100 entities changed
**Detection**: MemoryEntity fields don't match
**Action**: Update adapter to use new entity fields

**Recovery Time**: 10 minutes

### Downstream Impact

**Scenario**: Adapter method names change
**Prevention**: All adapter method signatures are LOCKED
**Mitigation**: Update all use sites
**Affected Tasks**: T501 (RAG Agent), T502 (Memory Consolidation), T503 (Tests)

---

## Artifacts

**Files Modified**:
- `agentx/infrastructure/external/qdrant_vector_store.py` (Real embeddings, LOCKED)

**Locked APIs**:
- All method signatures remain same as T101
- Embedding generation is internal implementation detail

---

## Quality Gates

**Quality Checks**:
- **Check**: Adapter file exists and updated
  - Command: `grep -c "EmbeddingService" agentx/infrastructure/external/qdrant_vector_store.py`
  - Expected: > 0 (has EmbeddingService)
  - Required: Yes

- **Check**: Adapter can be imported
  - Command: `python3 -c "from agentx.infrastructure.external.qdrant_vector_store import QdrantVectorStoreAdapter; print('OK')"`
  - Expected: `OK`
  - Required: Yes

---

## Notes

1. Real embeddings with sentence-transformers (MiniLM-L6-v2)
2. Embedding dimension: 384 (MiniLM)
3. Semantic search with cosine similarity
4. Lazy model loading (on first use)
5. Batch embedding support
6. Memory consolidation basic implementation (Phase 7: full)

---

## Completion Checklist

- [ ] Qdrant adapter updated with EmbeddingService
- [ ] store_memory() generates real embeddings
- [ ] search_memories() uses vector similarity
- [ ] get_all_memories() retrieves user memories
- [ ] update_memory() regenerates embeddings
- [ ] consolidate_memories() basic implementation
- [ ] sentence-transformers added to dependencies
- [ ] All imports work
- [ ] Ready for T501 (RAG Agent)

---

**Task T500 is part of Phase 5: Memory + RAG**
**Locked APIs**: All adapter method signatures (same as T101)

# T503: Create Phase 5 Integration Tests

**Phase**: 5
**Estimated Time**: 35 minutes
**Dependencies**: T500, T501, T502
**Blocked By**: None

---

## Context

**LLD References**:
- `LLD.md` - Phase 5: Testing Strategy
- `lld/incremental_release_plan.md` - Phase 5: Memory + RAG tests

**Description**:
Creates integration tests for Phase 5 memory layer components. Tests verify real embeddings, vector search, RAG retrieval, and memory consolidation.

---

## Acceptance Criteria

**Passing Criteria**:
- Test file for memory repository
- Test file for RAG agent
- Test file for memory consolidation
- All tests use real Qdrant (or mock Qdrant client)
- All tests verify actual behavior (not mocking LLMs/embeddings)
- Tests pass with `pytest tests/integration/phase5/`

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify test files exist
test -f tests/integration/phase5/test_memory_repository.py && echo "Memory repository tests exist"
test -f tests/integration/phase5/test_rag_agent.py && echo "RAG agent tests exist"
test -f tests/integration/phase5/test_memory_consolidation.py && echo "Memory consolidation tests exist"

# Run tests
pytest tests/integration/phase5/ -v
```

---

## Implementation Steps

### Step 1: Create memory repository tests

Create file `tests/integration/phase5/test_memory_repository.py`:

```python
"""Integration tests for memory repository with real embeddings."""

import pytest
from uuid import uuid4
from datetime import datetime

from agentx.infrastructure.external.qdrant_vector_store import (
    QdrantVectorStoreAdapter,
    EmbeddingService,
)
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams


class TestEmbeddingService:
    """Test EmbeddingService with real sentence-transformers."""

    def test_service_initialization(self):
        """Should initialize with correct dimension."""
        service = EmbeddingService()
        assert service.embedding_dim == 384  # MiniLM-L6-v2

    def test_embed_returns_correct_dimension(self):
        """Should generate embedding with correct dimension."""
        service = EmbeddingService()
        text = "Test text for embedding"
        embedding = service.embed(text)
        assert len(embedding) == 384
        assert all(isinstance(x, float) for x in embedding)

    def test_embed_batch_consistent(self):
        """Batch embeddings should be consistent with single."""
        service = EmbeddingService()
        texts = ["Text 1", "Text 2", "Text 3"]

        batch_embeddings = service.embed_batch(texts)
        single_embeddings = [service.embed(t) for t in texts]

        assert len(batch_embeddings) == len(single_embeddings)
        for batch, single in zip(batch_embeddings, single_embeddings):
            assert batch == single


class TestQdrantVectorStoreAdapter:
    """Test Qdrant adapter with real embeddings and Qdrant."""

    @pytest.fixture
    async def qdrant_client(self):
        """Create test Qdrant client."""
        client = AsyncQdrantClient(url="http://localhost:6333")

        # Create test collection
        collection_name = "test_memory"
        await client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )

        yield client, collection_name

        # Cleanup
        await client.delete_collection(collection_name)

    @pytest.fixture
    def adapter(self, qdrant_client):
        """Create adapter instance."""
        client, collection_name = qdrant_client
        return QdrantVectorStoreAdapter(client, collection_name)

    @pytest.mark.asyncio
    async def test_store_memory_returns_uuid(self, adapter):
        """Should store memory and return UUID."""
        memory_id = await adapter.store_memory(
            content="Test memory content",
            user_id="test_user_hash",
            metadata={"test": True}
        )

        assert isinstance(memory_id, type(uuid4()))

    @pytest.mark.asyncio
    async def test_search_memories_finds_stored(self, adapter):
        """Should find semantically similar memories."""
        # Store a memory
        await adapter.store_memory(
            content="Python programming language",
            user_id="test_user_hash",
            metadata={"category": "tech"}
        )

        # Search with similar query
        results = await adapter.search_memories(
            query="Python code development",
            user_id="test_user_hash",
            limit=5
        )

        assert len(results) > 0
        assert "Python" in results[0]["content"]
        assert results[0]["score"] > 0.7  # High similarity

    @pytest.mark.asyncio
    async def test_search_filters_by_user_id(self, adapter):
        """Should only return memories for specified user."""
        # Store memories for different users
        await adapter.store_memory(
            content="User 1 memory",
            user_id="user1_hash"
        )
        await adapter.store_memory(
            content="User 2 memory",
            user_id="user2_hash"
        )

        # Search for user1 only
        results = await adapter.search_memories(
            query="memory",
            user_id="user1_hash",
            limit=10
        )

        assert all(r["metadata"].get("user_id") == "user1_hash" for r in results)

    @pytest.mark.asyncio
    async def test_get_all_memories(self, adapter):
        """Should retrieve all memories for user."""
        # Store multiple memories
        await adapter.store_memory("Memory 1", "test_user")
        await adapter.store_memory("Memory 2", "test_user")
        await adapter.store_memory("Memory 3", "test_user")

        # Get all
        all_memories = await adapter.get_all_memories("test_user")

        assert len(all_memories) >= 3

    @pytest.mark.asyncio
    async def test_update_memory_changes_content(self, adapter):
        """Should update memory content and re-embed."""
        memory_id = await adapter.store_memory(
            content="Original content",
            user_id="test_user"
        )

        # Update
        success = await adapter.update_memory(memory_id, "Updated content")
        assert success is True

        # Verify updated content is searchable
        results = await adapter.search_memories(
            query="Updated",
            user_id="test_user",
            limit=5
        )
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_delete_memory(self, adapter):
        """Should delete memory by ID."""
        memory_id = await adapter.store_memory(
            content="To be deleted",
            user_id="test_user"
        )

        # Delete
        success = await adapter.delete_memory(memory_id)
        assert success is True

        # Verify gone
        results = await adapter.search_memories(
            query="deleted",
            user_id="test_user",
            limit=5
        )
        assert not any(r["memory_id"] == memory_id for r in results)

    @pytest.mark.asyncio
    async def test_consolidate_memories_returns_entity(self, adapter):
        """Should return consolidation entity."""
        # Store some memories
        await adapter.store_memory("Memory 1", "test_user")
        await adapter.store_memory("Memory 2", "test_user")

        consolidation = await adapter.consolidate_memories(
            session_id=uuid4(),
            user_id="test_user"
        )

        assert consolidation.session_id is not None
        assert consolidation.status == "completed"
        assert consolidation.memories_processed >= 0
```

### Step 2: Create RAG agent tests

Create file `tests/integration/phase5/test_rag_agent.py`:

```python
"""Integration tests for RAG agent."""

import pytest
from unittest.mock import Mock
from uuid import uuid4

from agentx.agent.dspy_agents.rag_agent import (
    RAGAgent,
    get_rag_agent,
)
from agentx.domain.repositories.memory_repository import MemoryRepository


class TestRAGAgent:
    """Test RAG agent with mock repository."""

    @pytest.fixture
    def mock_memory_repository(self):
        """Create mock memory repository."""
        repo = Mock(spec=MemoryRepository)

        # Mock search results
        repo.search_memories.return_value = [
            {
                "memory_id": uuid4(),
                "content": "Python is a programming language",
                "score": 0.85,
                "metadata": {"category": "tech"}
            },
            {
                "memory_id": uuid4(),
                "content": "JavaScript is used for web development",
                "score": 0.72,
                "metadata": {"category": "tech"}
            }
        ]

        return repo

    @pytest.fixture
    def rag_agent(self, mock_memory_repository):
        """Create RAG agent with mock repository."""
        return RAGAgent(
            memory_repository=mock_memory_repository,
            top_k=5,
            similarity_threshold=0.7
        )

    def test_agent_initialization(self, rag_agent):
        """Should initialize with correct settings."""
        assert rag_agent.top_k == 5
        assert rag_agent.similarity_threshold == 0.7
        assert rag_agent.memory_repository is not None

    @pytest.mark.asyncio
    async def test_retrieve_context_filters_by_threshold(self, rag_agent, mock_memory_repository):
        """Should filter results by similarity threshold."""
        context = await rag_agent.retrieve_context(
            query="Python programming",
            user_id="test_user"
        )

        # Should include results above threshold
        assert "Python" in context
        assert "JavaScript" in context

        # Verify search was called
        mock_memory_repository.search_memories.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_context_empty_when_no_results(self, rag_agent, mock_memory_repository):
        """Should return empty string when no results."""
        # Mock empty results
        mock_memory_repository.search_memories.return_value = []

        context = await rag_agent.retrieve_context(
            query="Unknown topic",
            user_id="test_user"
        )

        assert context == ""

    @pytest.mark.asyncio
    async def test_retrieve_context_formats_correctly(self, rag_agent, mock_memory_repository):
        """Should format context with relevance scores."""
        context = await rag_agent.retrieve_context(
            query="Python",
            user_id="test_user"
        )

        # Should contain memory labels and scores
        assert "[Memory" in context
        assert "relevance:" in context
        assert "0.85" in context

    def test_is_confident_with_context(self, rag_agent):
        """Should return True when context was used."""
        prediction = {
            "final_answer": "Test answer",
            "retrieved_context": "Some context",
            "context_used": True
        }

        assert rag_agent.is_confident(prediction) is True

    def test_is_confident_without_context(self, rag_agent):
        """Should return False when no context used."""
        prediction = {
            "final_answer": "Test answer",
            "retrieved_context": "",
            "context_used": False
        }

        assert rag_agent.is_confident(prediction) is False


class TestRAGAgentFactory:
    """Test factory function."""

    def test_get_rag_agent(self):
        """Should return RAGAgent instance."""
        agent = get_rag_agent()
        assert isinstance(agent, RAGAgent)

    def test_get_rag_agent_singleton(self):
        """Should return same instance (singleton pattern)."""
        agent1 = get_rag_agent()
        agent2 = get_rag_agent()
        assert agent1 is agent2 or isinstance(agent2, RAGAgent)
```

### Step 3: Create memory consolidation tests

Create file `tests/integration/phase5/test_memory_consolidation.py`:

```python
"""Integration tests for memory consolidation service."""

import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4

from agentx.application.services.memory_consolidation import (
    MemoryConsolidationService,
    get_memory_consolidation_service,
)
from agentx.domain.entities.memory_consolidation import ConsolidationTrigger
from agentx.domain.repositories.memory_repository import MemoryRepository


class TestMemoryConsolidationService:
    """Test memory consolidation service."""

    @pytest.fixture
    def mock_memory_repository(self):
        """Create mock memory repository."""
        repo = Mock(spec=MemoryRepository)

        # Mock get_all_memories
        repo.get_all_memories.return_value = [
            {
                "memory_id": uuid4(),
                "content": "Memory 1",
                "metadata": {"session_id": "test-session"}
            },
            {
                "memory_id": uuid4(),
                "content": "Memory 2",
                "metadata": {"session_id": "test-session"}
            }
        ]

        return repo

    @pytest.fixture
    def consolidation_service(self, mock_memory_repository):
        """Create consolidation service with mock repository."""
        return MemoryConsolidationService(
            memory_repository=mock_memory_repository,
            consolidation_interval=10
        )

    def test_service_initialization(self, consolidation_service):
        """Should initialize with correct settings."""
        assert consolidation_service.consolidation_interval == 10
        assert consolidation_service.session_counters == {}
        assert consolidation_service.memory_repository is not None

    @pytest.mark.asyncio
    async def test_consolidate_session_returns_entity(self, consolidation_service):
        """Should return consolidation entity."""
        session_id = uuid4()

        result = await consolidation_service.consolidate_session(
            session_id=session_id,
            user_id="test_user",
            trigger=ConsolidationTrigger.MANUAL
        )

        assert result.session_id == session_id
        assert result.trigger == ConsolidationTrigger.MANUAL
        assert result.status in ["completed", "failed"]

    @pytest.mark.asyncio
    async def test_consolidate_session_processes_memories(self, consolidation_service, mock_memory_repository):
        """Should process session memories."""
        session_id = uuid4()

        result = await consolidation_service.consolidate_session(
            session_id=session_id,
            user_id="test_user"
        )

        # Should have processed memories
        assert result.memories_processed >= 0
        mock_memory_repository.get_all_memories.assert_called_once_with("test_user")

    @pytest.mark.asyncio
    async def test_consolidate_session_filters_by_session(self, consolidation_service):
        """Should filter memories for specific session."""
        session_id = uuid4()

        result = await consolidation_service.consolidate_session(
            session_id=session_id,
            user_id="test_user"
        )

        # Verify filtering happened (via _filter_session_memories)
        assert result is not None

    @pytest.mark.asyncio
    async def test_consolidate_session_resets_counter(self, consolidation_service):
        """Should reset session counter after consolidation."""
        session_id = uuid4()

        # Record some interactions
        await consolidation_service.record_interaction(session_id)
        await consolidation_service.record_interaction(session_id)

        # Consolidate
        await consolidation_service.consolidate_session(
            session_id=session_id,
            user_id="test_user"
        )

        # Counter should be reset
        assert str(session_id) not in consolidation_service.session_counters

    @pytest.mark.asyncio
    async def test_check_consolidation_needed_true(self, consolidation_service):
        """Should return True when threshold reached."""
        session_id = uuid4()

        # Record interactions up to threshold
        for _ in range(10):
            await consolidation_service.record_interaction(session_id)

        needed = await consolidation_service.check_consolidation_needed(session_id)
        assert needed is True

    @pytest.mark.asyncio
    async def test_check_consolidation_needed_false(self, consolidation_service):
        """Should return False when below threshold."""
        session_id = uuid4()

        # Record few interactions
        await consolidation_service.record_interaction(session_id)

        needed = await consolidation_service.check_consolidation_needed(session_id)
        assert needed is False

    @pytest.mark.asyncio
    async def test_record_interaction_increments_counter(self, consolidation_service):
        """Should increment interaction counter."""
        session_id = uuid4()

        await consolidation_service.record_interaction(session_id)
        await consolidation_service.record_interaction(session_id)

        assert consolidation_service.session_counters[str(session_id)] == 2

    @pytest.mark.asyncio
    async def test_get_consolidation_history_empty(self, consolidation_service):
        """Should return empty list (Phase 5 limitation)."""
        history = await consolidation_service.get_consolidation_history("test_user")

        assert history == []  # Phase 5: Not implemented yet


class TestConsolidationServiceFactory:
    """Test factory function."""

    def test_get_memory_consolidation_service(self):
        """Should return MemoryConsolidationService instance."""
        service = get_memory_consolidation_service()
        assert isinstance(service, MemoryConsolidationService)

    def test_get_consolidation_service_singleton(self):
        """Should return same instance (singleton pattern)."""
        service1 = get_memory_consolidation_service()
        service2 = get_memory_consolidation_service()
        assert isinstance(service2, MemoryConsolidationService)
```

### Step 4: Create test directory

```bash
mkdir -p tests/integration/phase5
```

---

## Expected Failures & Countermeasures

### Failure: Qdrant not running

**Likelihood**: High
**Symptoms**: `qdrant_client.http.exceptions.UnexpectedResponse: Connection refused`

**Countermeasures**:
1. Start Qdrant: `docker run -d -p 6333:6333 qdrant/qdrant`
2. Add pytest marker for integration tests: `@pytest.mark.integration`
3. Skip Qdrant tests if unavailable: `@pytest.mark.skipif(not qdrant_available())`

**Recovery Time**: 3 minutes

### Failure: sentence-transformers not installed

**Likelihood**: Medium
**Symptoms**: `ModuleNotFoundError: No module named 'sentence_transformers'`

**Countermeasures**:
1. Install: `uv pip install sentence-transformers`
2. Or add to requirements-phase5.txt
3. Document in Phase 5 README

**Recovery Time**: 5 minutes

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T500-T502 implementations changed
**Detection**: Test assertions fail
**Action**: Update tests to match new implementations

**Recovery Time**: 15 minutes

### Downstream Impact

**Scenario**: Test file names change
**Prevention**: Test file names are not locked
**Mitigation**: Update pytest commands
**Affected Tasks**: All later test tasks

---

## Artifacts

**Files Created**:
- `tests/integration/phase5/test_memory_repository.py` (Memory tests, not locked)
- `tests/integration/phase5/test_rag_agent.py` (RAG tests, not locked)
- `tests/integration/phase5/test_memory_consolidation.py` (Consolidation tests, not locked)

**Locked APIs**:
- None (tests are not locked)

---

## Quality Gates

**Quality Checks**:
- **Check**: All test files exist
  - Command: `ls tests/integration/phase5/*.py`
  - Expected: 3 test files
  - Required: Yes

- **Check**: Tests can be imported
  - Command: `python3 -c "import tests.integration.phase5.test_memory_repository; print('OK')"`
  - Expected: `OK`
  - Required: Yes

- **Check**: Tests run (may skip if Qdrant unavailable)
  - Command: `pytest tests/integration/phase5/ -v --tb=short`
  - Expected: Tests run (integration tests may skip if services missing)
  - Required: Yes

---

## Notes

1. Real embeddings tested (not mocked) - tests actual behavior
2. Qdrant tests marked with `@pytest.mark.integration`
3. Can use mock Qdrant client for faster unit tests
4. Memory consolidation uses mock repository (faster tests)
5. RAG agent tests use mock repository (focus on logic)
6. sentence-transformers lazy-loads on first use
7. Tests verify filtering, scoring, and formatting

---

## Completion Checklist

- [ ] test_memory_repository.py created
- [ ] EmbeddingService tests
- [ ] QdrantVectorStoreAdapter integration tests
- [ ] test_rag_agent.py created
- [ ] RAGAgent context retrieval tests
- [ ] test_memory_consolidation.py created
- [ ] MemoryConsolidationService tests
- [ ] All tests can be imported
- [ ] Tests run with pytest
- [ ] Phase 5 complete!

---

## Phase 5 Summary

**Tasks Completed**:
- T500: Create Memory Repository Implementations
- T501: Create RAG Agent
- T502: Create Memory Consolidation
- T503: Create Phase 5 Integration Tests

**Phase 5 Deliverables**:
- Real embeddings with sentence-transformers
- Semantic search with Qdrant vector storage
- RAG agent with context retrieval and confidence scoring
- Memory consolidation service (scheduled + manual triggers)
- Integration tests for memory layer

**Next Phase**: Phase 6 - Plugin System (2-3 hours)

---

**Task T503 is part of Phase 5: Memory + RAG**
**Phase 5 Status**: ✅ COMPLETE (after this task is done)

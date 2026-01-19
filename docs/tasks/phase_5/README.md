# Phase 5 Tasks: Memory + RAG

**Phase**: 5
**Estimated Time**: 2-3 hours
**Dependencies**: Phase 0-4 complete
**Status**: Ready for Execution

---

## Phase Overview

Phase 5 implements memory consolidation and RAG (Retrieval-Augmented Generation) for context-aware agent responses. This enables the agent to remember previous conversations and retrieve relevant context before answering.

### What's Implemented

- **Memory Repository**: Real embeddings with sentence-transformers
- **Qdrant Vector Store**: Semantic search with cosine similarity
- **RAG Agent**: Context retrieval with confidence scoring
- **Memory Consolidation**: Scheduled and manual triggers

### What's Stubbed

- Plugin system - Phase 6
- Full memory summarization with LLM - Phase 7

---

## Task List

### T500: Create Memory Repository Implementations (50 minutes)

**File**: `T500_memory_repository.md`

**Creates**:
- `infrastructure/external/qdrant_vector_store.py`
  - EmbeddingService - sentence-transformers (MiniLM-L6-v2)
  - QdrantVectorStoreAdapter - real embeddings, vector search
  - store_memory() - Generate embeddings and store
  - search_memories() - Semantic similarity search
  - get_all_memories() - Retrieve user memories
  - update_memory() - Re-embed on update
  - delete_memory() - Remove memory
  - consolidate_memories() - Basic consolidation (Phase 7: full)

---

### T501: Create RAG Agent (40 minutes)

**File**: `T501_rag_agent.md`

**Creates**:
- `agent/dspy_agents/rag_agent.py`
  - RAGAgent class
  - retrieve_context() - Search memories with threshold
  - query() - Full RAG flow (retrieve + generate)
  - is_confident() - Check if context was used
  - get_rag_agent() - Factory function

---

### T502: Create Memory Consolidation (45 minutes)

**File**: `T502_memory_consolidation.md`

**Creates**:
- `application/services/memory_consolidation.py`
  - MemoryConsolidationService class
  - consolidate_session() - Manual/scheduled consolidation
  - check_consolidation_needed() - Check trigger threshold
  - record_interaction() - Track for auto-trigger
  - get_consolidation_history() - Get past consolidations (Phase 7: full)
- `application/services/__init__.py` - Package exports

---

### T503: Create Phase 5 Integration Tests (35 minutes)

**File**: `T503_phase5_tests.md`

**Creates**:
- `tests/integration/phase5/test_memory_repository.py`
  - EmbeddingService tests
  - QdrantVectorStoreAdapter integration tests
- `tests/integration/phase5/test_rag_agent.py`
  - RAGAgent context retrieval tests
- `tests/integration/phase5/test_memory_consolidation.py`
  - MemoryConsolidationService tests

---

## Running Phase 5

### Prerequisites

1. **Phase 0 Complete**: T001-T009
2. **Phase 1 Complete**: T100-T104
3. **Phase 2 Complete**: T200-T204
4. **Phase 3 Complete**: T300-T304
5. **Phase 4 Complete**: T400-T403

### Execution Order

```bash
# T500: Memory Repository Implementations
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend
# Follow T500_memory_repository.md

# T501: RAG Agent
# Follow T501_rag_agent.md

# T502: Memory Consolidation
# Follow T502_memory_consolidation.md

# T503: Phase 5 Tests
# Follow T503_phase5_tests.md
```

### Verification (End of Phase 5)

```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify embeddings service
python3 -c "from agentx.infrastructure.external.qdrant_vector_store import EmbeddingService; e = EmbeddingService(); print(f'Embedding dim: {e.embedding_dim}')"

# Verify Qdrant adapter
python3 -c "from agentx.infrastructure.external.qdrant_vector_store import QdrantVectorStoreAdapter; print('Qdrant adapter OK')"

# Verify RAG agent
python3 -c "from agentx.agent.dspy_agents.rag_agent import RAGAgent; print('RAG agent OK')"

# Verify memory consolidation
python3 -c "from agentx.application.services.memory_consolidation import MemoryConsolidationService; print('Consolidation service OK')"

# Run tests
pytest tests/integration/phase5/ -v
```

---

## Phase 5 Deliverables

### Infrastructure Layer

**Qdrant Vector Store** (1 file):
- ✅ `qdrant_vector_store.py` - Real embeddings, semantic search

### Agent Layer

**RAG Agent** (1 file):
- ✅ `rag_agent.py` - Context retrieval and generation

### Application Layer

**Services** (2 files):
- ✅ `memory_consolidation.py` - Consolidation service
- ✅ `services/__init__.py` - Package exports

### Testing

**Integration Tests** (3 files):
- ✅ `test_memory_repository.py`
- ✅ `test_rag_agent.py`
- ✅ `test_memory_consolidation.py`

**Total**: 7 files created/updated in Phase 5

---

## Key Features

### Real Embeddings

```
Text → sentence-transformers (MiniLM-L6-v2) → 384-dim vector → Qdrant
```

### Semantic Search

```
Query → Embed → Cosine Similarity → Top-K Results → Filter by Threshold
```

### RAG Flow

```
User Query
    ↓
Retrieve Context (if similar memories exist)
    ↓
Generate Answer with Context
    ↓
Score Confidence
```

### Memory Consolidation

```
Every 10 interactions
    ↓
Summarize and merge memories
    ↓
Invalidate old memories
    ↓
Store consolidated memory
```

---

## Next Phase: Phase 6 - Plugin System

**Phase 6 Tasks** (T600-T603):
- T600: Create Plugin Interface
- T601: Create Plugin Permissions
- T602: Create Plugin Registration
- T603: Create Phase 6 Tests

**Phase 6 Deliverables**:
- Plugin interface (ABC)
- Plugin permissions model
- Plugin registration and lifecycle
- Integration tests for plugin system

---

## Dependencies Required

```bash
# Add to requirements.txt or install separately
uv pip install sentence-transformers
uv pip install qdrant-client

# Optional: for faster embeddings
uv pip install sentence-transformers[fast]
```

---

## External Services

### Qdrant (Required for Phase 5)

```bash
# Start Qdrant with Docker
docker run -d -p 6333:6333 qdrant/qdrant

# Or use Qdrant Cloud
# Set QDRANT_URL in .env
```

---

## Configuration

### .env Settings

```bash
# Qdrant configuration
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=agentx_memories

# Embedding configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIM=384

# RAG configuration
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.7

# Consolidation configuration
CONSOLIDATION_INTERVAL=10
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────┐
│          Main DSPy Agent               │
│    (from Phase 2: T202)                │
└──────────────┬──────────────────────────┘
               │
               │ Retrieves context
               ▼
┌─────────────────────────────────────────┐
│            RAG Agent                    │
│         (T501: new)                     │
│  ┌──────────────────────────────────┐  │
│  │ retrieve_context()               │  │
│  │ - Search by semantic similarity  │  │
│  │ - Filter by threshold            │  │
│  │ - Format with scores             │  │
│  └──────────────────────────────────┘  │
└──────────────┬──────────────────────────┘
               │
               │ Searches memories
               ▼
┌─────────────────────────────────────────┐
│      Qdrant Vector Store                │
│   (T500: updated with embeddings)       │
│  ┌──────────────────────────────────┐  │
│  │ EmbeddingService                 │  │
│  │ - sentence-transformers          │  │
│  │ - 384-dim vectors                │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │ QdrantVectorStoreAdapter         │  │
│  │ - store_memory()                 │  │
│  │ - search_memories()              │  │
│  │ - get_all_memories()             │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
               │
               │ Periodic consolidation
               ▼
┌─────────────────────────────────────────┐
│    Memory Consolidation Service         │
│        (T502: new)                      │
│  ┌──────────────────────────────────┐  │
│  │ consolidate_session()            │  │
│  │ - Process session memories       │  │
│  │ - Merge and summarize            │  │
│  │ - Invalidate old memories        │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │ record_interaction()             │  │
│  │ - Track for auto-trigger         │  │
│  │ - Trigger every N interactions   │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

---

## Testing Strategy

### What Gets Tested

1. **EmbeddingService**: Real embeddings, correct dimensions
2. **QdrantVectorStoreAdapter**: Store, search, update, delete
3. **RAGAgent**: Context retrieval, filtering, confidence
4. **MemoryConsolidationService**: Triggers, counters, consolidation

### What Uses Mocks

- Memory repository in RAG tests (faster)
- Memory repository in consolidation tests (faster)

### What Uses Real Services

- Qdrant in integration tests (requires running Qdrant)
- Embeddings in integration tests (actual sentence-transformers)

---

## Common Issues

### Issue: "No module named 'sentence_transformers'"

**Solution**:
```bash
uv pip install sentence-transformers
```

### Issue: Qdrant connection refused

**Solution**:
```bash
# Start Qdrant
docker run -d -p 6333:6333 qdrant/qdrant

# Verify
curl http://localhost:6333/
```

### Issue: Embeddings too slow

**Solution**:
```bash
# Use faster version
uv pip install sentence-transformers[fast]

# Or use GPU (if available)
CUDA_VISIBLE_DEVICES=0 python
```

---

## Performance Considerations

### Embedding Generation

- **Latency**: ~50-100ms per text (CPU), ~10-20ms (GPU)
- **Batch Processing**: Use `embed_batch()` for multiple texts
- **Caching**: Cache embeddings for repeated queries

### Vector Search

- **Latency**: ~10-50ms for 100K vectors (Qdrant)
- **Indexing**: Automatic HNSW indexing in Qdrant
- **Tuning**: Adjust `ef_construct` for speed/accuracy tradeoff

### Memory Consolidation

- **Frequency**: Every 10 interactions (configurable)
- **Cost**: Depends on memory count
- **Phase 7**: Full LLM-based summarization

---

## Future Enhancements (Phase 7)

- **Full Summarization**: LLM-based memory consolidation
- **Memory Types**: Episodic, semantic, procedural
- **Memory Hierarchy**: Short-term, mid-term, long-term
- **Memory Forgetting**: TTL-based expiration
- **Memory Importance Scoring**: Prioritize important memories

---

**Phase 5 Status**: ✅ READY FOR EXECUTION

**All task files created**: T500-T503

**Total Estimated Time**: 2-3 hours

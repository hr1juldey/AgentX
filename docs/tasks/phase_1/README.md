# Phase 1 Tasks: Domain + Infrastructure

**Phase**: 1
**Estimated Time**: 2-3 hours
**Dependencies**: Phase 0 (T001-T009)
**Status**: Ready for Execution

---

## Phase Overview

Phase 1 implements the foundational domain entities and infrastructure adapters. This includes all repository implementations with real storage backends (Qdrant, Redis, SQLite) and the Ollama LLM adapter.

### What's Implemented

- **Domain Layer**: All entity classes with business logic
- **Infrastructure Layer**: Qdrant, Redis, SQLite, In-Memory adapters
- **External Services**: Ollama LLM adapter with streaming
- **Dependency Injection**: Updated DI container with Phase 1 adapters
- **Testing**: Integration tests for all Phase 1 components

### What's Stubbed

- Agent logic (DSPy agents, tools) - Phase 2
- UI descriptors (Pydantic models) - Phase 3
- WebSocket endpoints - Phase 3
- Memory consolidation (full implementation) - Phase 5

---

## Task List

### T100: Create Domain Entities (40 minutes)

**File**: `T100_create_entities.md`

**Creates**:
- `agentx/domain/entities/enums.py` - SessionState, UIComponentType, ConsolidationStatus, etc.
- `agentx/domain/entities/agent_session.py` - AgentSessionEntity with state transitions
- `agentx/domain/entities/ui_component.py` - UIComponentEntity with lifecycle
- `agentx/domain/entities/memory_consolidation.py` - MemoryConsolidationEntity
- `agentx/domain/entities/conversation_turn.py` - ConversationTurnEntity
- `agentx/domain/entities/memory.py` - MemoryEntity with embeddings and TTL
- `agentx/domain/entities/user.py` - UserEntity with SHA-256 hashed ID

**Locked APIs**:
- All entity class names
- All entity field names and types
- All entity business method signatures

**Verification**:
```bash
python3 -c "from agentx.domain.entities import AgentSessionEntity, UIComponentEntity, MemoryEntity; print('OK')"
```

---

### T101: Create Repository Implementations (50 minutes)

**File**: `T101_repository_implementations.md`

**Creates**:
- `agentx/infrastructure/external/qdrant_vector_store.py` - QdrantVectorStoreAdapter
- `agentx/infrastructure/external/redis_session_adapter.py` - RedisSessionAdapter
- `agentx/infrastructure/external/sqlite_session_adapter.py` - SQLiteSessionAdapter
- `agentx/infrastructure/external/in_memory_ui_repository.py` - InMemoryUIComponentRepository

**Locked APIs**:
- All adapter class names
- All adapter method signatures (inherited from repository interfaces)

**Verification**:
```bash
python3 -c "from agentx.infrastructure.external import QdrantVectorStoreAdapter, RedisSessionAdapter, SQLiteSessionAdapter; print('OK')"
```

---

### T102: Create Ollama LLM Adapter (30 minutes)

**File**: `T102_ollama_llm_adapter.md`

**Creates**:
- `agentx/infrastructure/external/ollama_llm.py` - OllamaLLMAdapter with streaming

**Features**:
- `generate_response()` - Non-streaming text generation
- `stream_response()` - Async iterator for streaming
- `health_check()` - Monitoring support
- `list_models()` - Model discovery

**Locked APIs**:
- `OllamaLLMAdapter` class name
- Method signatures for `generate_response()`, `stream_response()`

**Verification**:
```bash
python3 -c "from agentx.infrastructure.external.ollama_llm import OllamaLLMAdapter; a = OllamaLLMAdapter('http://localhost:11434', 'gemma3:4b'); print(repr(a))"
```

---

### T103: Update Dependency Injection Container (25 minutes)

**File**: `T103_update_di_container.md`

**Updates**:
- `agentx/core/dependencies.py` - Complete rewrite with Phase 1 adapters

**Getter Functions**:
- `get_qdrant_adapter()` - Qdrant vector store
- `get_redis_adapter()` - Redis session storage
- `get_sqlite_adapter()` - SQLite long-term storage
- `get_session_repository()` - Redis → SQLite fallback
- `get_ui_repository()` - In-memory UI components
- `get_ollama_adapter()` - Ollama LLM

**Setter Functions** (for testing):
- `set_qdrant_adapter()`, `set_redis_adapter()`, etc.
- `reset_dependencies()` - Cleanup for tests

**Locked APIs**:
- All getter/setter function signatures

**Verification**:
```bash
python3 -c "from agentx.core.dependencies import get_qdrant_adapter, get_redis_adapter, get_ollama_adapter; print('OK')"
```

---

### T104: Create Phase 1 Integration Tests (40 minutes)

**File**: `T104_phase1_integration_tests.md`

**Creates**:
- `tests/integration/phase1/test_entities.py` - Entity state transition tests
- `tests/integration/phase1/test_sqlite_adapter.py` - SQLite CRUD tests
- `tests/integration/phase1/test_ui_repository.py` - In-memory repository tests
- `tests/integration/phase1/test_ollama_adapter.py` - Ollama adapter tests (mocked)
- `tests/conftest.py` - Updated with Phase 1 fixtures

**Test Categories**:
- Entity business logic (state transitions)
- SQLite persistence
- In-memory repository operations
- Ollama adapter (mocked, optional real service tests)

**Verification**:
```bash
pytest tests/integration/phase1/ -v
```

---

## Running Phase 1

### Prerequisites

1. **Phase 0 Complete**: All tasks T001-T009 must be complete
2. **Dependencies Installed**: `uv pip install -r requirements.txt`
3. **Optional Services** (for full integration tests):
   - Ollama: `ollama serve && ollama pull gemma3:4b`
   - Redis: `docker run -d -p 6379:6379 redis:alpine`
   - Qdrant: `docker run -d -p 6333:6333 qdrant/qdrant`

### Execution Order

Execute tasks in order:

```bash
# T100: Domain Entities
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend
# Follow T100_create_entities.md

# T101: Repository Implementations
# Follow T101_repository_implementations.md

# T102: Ollama Adapter
# Follow T102_ollama_llm_adapter.md

# T103: Update DI Container
# Follow T103_update_di_container.md

# T104: Integration Tests
# Follow T104_phase1_integration_tests.md
```

### Verification (End of Phase 1)

```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify all entities import
python3 -c "from agentx.domain.entities import AgentSessionEntity, UIComponentEntity, MemoryEntity, MemoryConsolidationEntity; print('Entities OK')"

# Verify all adapters import
python3 -c "from agentx.infrastructure.external import QdrantVectorStoreAdapter, RedisSessionAdapter, SQLiteSessionAdapter, OllamaLLMAdapter; print('Adapters OK')"

# Verify DI container
python3 -c "from agentx.core.dependencies import get_qdrant_adapter, get_ollama_adapter; print('DI OK')"

# Run tests (skip tests requiring real services)
pytest tests/integration/phase1/ -v
```

---

## Phase 1 Deliverables

### Domain Layer

**Entities** (7 files):
- ✅ `enums.py` - All enumerations
- ✅ `agent_session.py` - Session entity with state transitions
- ✅ `ui_component.py` - UI component entity with lifecycle
- ✅ `memory_consolidation.py` - Consolidation entity
- ✅ `conversation_turn.py` - Conversation turn entity
- ✅ `memory.py` - Memory entity with embeddings and TTL
- ✅ `user.py` - User entity with hashed ID

### Infrastructure Layer

**Adapters** (4 files):
- ✅ `qdrant_vector_store.py` - Vector storage
- ✅ `redis_session_adapter.py` - Fast session storage
- ✅ `sqlite_session_adapter.py` - Persistent storage
- ✅ `in_memory_ui_repository.py` - Session-scoped UI state

### External Services

**LLM** (1 file):
- ✅ `ollama_llm.py` - Ollama adapter with streaming

### Dependency Injection

**DI Container** (1 file updated):
- ✅ `core/dependencies.py` - All Phase 1 getters

### Testing

**Integration Tests** (4 files):
- ✅ `test_entities.py` - Entity tests
- ✅ `test_sqlite_adapter.py` - SQLite tests
- ✅ `test_ui_repository.py` - UI repository tests
- ✅ `test_ollama_adapter.py` - Ollama tests

**Total**: 17 files created/updated in Phase 1

---

## Next Phase: Phase 2 - Main DSPy Agent (2-3 hours)

After completing Phase 1, proceed to:

**Phase 2 Tasks** (T200-T299):
- T200: Create DSPy Signatures
- T201: Create DSPy Tools
- T202: Create Main DSPy ReAct Agent
- T203: Create Agent Use Cases
- T204: Create Phase 2 Tests

**Phase 2 Deliverables**:
- Main DSPy ReAct agent with tools
- Calculator, search, weather tools
- Agent use cases (ExecuteAgentQueryUseCase)
- Integration tests with real DSPy + Ollama

---

## Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'domain.entities'`

**Solution**:
1. Ensure T001 (directory structure) is complete
2. Check you're in the correct directory: `cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend`
3. Verify all `__init__.py` files exist

### Redis Connection Refused

**Problem**: `redis.exceptions.ConnectionError`

**Solution**:
1. Start Redis: `docker run -d -p 6379:6379 redis:alpine`
2. Or use system Redis: `sudo systemctl start redis`
3. Tests will fall back to SQLite if Redis unavailable

### Qdrant Not Installed

**Problem**: `ModuleNotFoundError: No module named 'qdrant_client'`

**Solution**:
1. Install qdrant-client: `uv pip install qdrant-client`
2. Or skip Qdrant tests: `pytest tests/integration/phase1/ -k "not qdrant"`

### Ollama Not Running

**Problem**: `httpx.ConnectError: Connection refused` for Ollama

**Solution**:
1. Ollama adapter tests are mocked (no real service needed)
2. For optional real tests: `ollama serve && ollama pull gemma3:4b`
3. Update test to enable real tests: `@pytest.mark.skipif(False, ...)`

---

**Phase 1 Status**: ✅ READY FOR EXECUTION

**All task files created**: T100-T104

**Total Estimated Time**: 2-3 hours

**Ready for Ralph Loop execution**

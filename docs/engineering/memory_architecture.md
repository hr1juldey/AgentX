# Memory Architecture

## Overview

AGENTX uses a **hybrid 2-tier memory architecture** with Mem0AI for intelligent consolidation and Qdrant + ColBERTv2 for semantic vector search.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AGENTX Memory System                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Application Layer                         │   │
│  │  (DSPy Agents, Tools, Voice Gateway)                        │   │
│  └────────────────────────┬────────────────────────────────────┘   │
│                           │                                         │
│                           ▼                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                  UnifiedMem0Adapter                         │   │
│  │  - Quality filtering (configurable thresholds)              │   │
│  │  - Consolidation (Mem0 duplicate detection)                 │   │
│  │  - Degraded mode fallback (local-only on Qdrant failure)    │   │
│  └────────────────┬──────────────────────────┬─────────────────┘   │
│                   │                          │                         │
│                   ▼                          ▼                         │
│  ┌──────────────────────────┐  ┌──────────────────────────────────┐ │
│  │       Mem0AI Client      │  │      Qdrant Vector Store        │ │
│  │  - LLM: Ollama gemma3:4b │  │  - ColBERTv2 embeddings         │ │
│  │  - History: Local        │  │  - Multi-vector (token-level)   │ │
│  │  - Consolidation         │  │  - 128-dim vectors              │ │
│  └──────────────────────────┘  └──────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Tiers

### Tier 1: Session Memory (In-Memory)
- **Location**: Application memory (ConversationStateManager)
- **Purpose**: Temporary storage of current session context
- **Duration**: Session lifetime
- **Content**: Recent messages, current topic, language preference

### Tier 2: Persistent Memory (Qdrant + ColBERTv2)
- **Location**: Qdrant vector database
- **Purpose**: Long-term semantic storage with retrieval
- **Duration**: Persistent (TTL-configurable)
- **Content**: User preferences, patterns, consolidated memories
- **Search**: ColBERTv2 late interaction (token-level granularity)

### Tier 3: Consolidated Memory (Mem0AI)
- **Location**: Abstracted by Mem0AI (stored in Qdrant)
- **Purpose**: Intelligent summarization and deduplication
- **Mechanism**: Mem0's built-in consolidation (LLM-powered)
- **Trigger**: When memory count exceeds `consolidation_threshold`

## Key Components

### UnifiedMem0Adapter
**File**: `infrastructure/memory/unified_mem0_adapter.py`

**Responsibilities**:
- Single source of truth for all Mem0 operations
- Quality-based filtering (prevents memory hoarding)
- Consolidation (via Mem0's duplicate detection)
- Degraded mode fallback when Qdrant unavailable

**Configuration** (from `memory_config.py`):
```python
quality_threshold: float = 0.6        # Min confidence for storage
min_result_length: int = 50           # Min chars for storage
consolidation_threshold: int = 100    # Trigger consolidation
```

**Degraded Mode**:
- Falls back to local-only storage if Qdrant unavailable
- Returns recent memories without semantic search
- Logs warnings for debugging

### ColBERT Embedding
**File**: `infrastructure/external/colbert/embedding.py`

**Model**: `colbert-ir/colbertv2.0`
**Vector Size**: 128 dimensions per token
**Multi-vector**: Each token → separate 128-dim vector (late interaction)

**Why ColBERT?**
- Token-level granularity (preserves fine-grained semantics)
- Late interaction (MaxSim operation for efficient retrieval)
- State-of-the-art retrieval performance

### Qdrant Vector Store
**File**: `infrastructure/database/qdrant/qdrant_vector_store.py`

**Collections**:
- `mem_tier2_` prefix for persistent memory
- Multi-vector storage (ColBERT multivectors)
- Filtered by `user_id` payload

### DSPy Retrieval
**File**: `infrastructure/retrieval/mem0_dspy_retriever.py`

**Integrates with**: DSPy RM (Retrieval Model) configuration

**Returns**: `list[str]` (text content only, filtered by quality)

## Data Flow

### Storing a Memory
```
1. Application calls UnifiedMem0Adapter.store_execution_result()
2. Quality check: confidence >= quality_threshold?
3. Quality check: length >= min_result_length?
4. Duplicate check: search for existing identical memory
5. If passes: Mem0.add() → Qdrant with ColBERT embeddings
6. If Qdrant fails: Degraded mode (local-only storage)
```

### Retrieving Memories
```
1. Application calls UnifiedMem0Adapter.search_memories()
2. If degraded mode: Return recent memories (no semantic search)
3. If normal mode:
   a. Qdrant search with ColBERT query embedding
   b. Return results with scores
4. Convert Mem0 "memory" key → "content" key
```

### Consolidation
```
1. Background check: memory_count > consolidation_threshold?
2. If yes: Trigger Mem0 consolidation
3. Mem0 merges similar memories (LLM-powered)
4. Consolidated memories stored back to Qdrant
```

## Configuration

### Memory Config
**File**: `core/memory_config.py`

```python
class MemoryConfig(BaseSettings):
    # Qdrant settings
    qdrant_url: str = "http://localhost:6335"

    # ColBERT settings
    colbert_model_name: str = "colbert-ir/colbertv2.0"
    colbert_vector_size: int = 128

    # Quality thresholds
    quality_threshold: float = 0.6
    min_result_length: int = 50
    consolidation_threshold: int = 100
```

**Environment Variables** (prefix: `MEMORY__`):
- `MEMORY__QDRANT_URL`
- `MEMORY__COLBERT_MODEL_NAME`
- `MEMORY__QUALITY_THRESHOLD`
- etc.

## API Examples

### Using UnifiedMem0Adapter

```python
from agentx.infrastructure.memory import UnifiedMem0Adapter

# Initialize (with degraded mode enabled by default)
adapter = UnifiedMem0Adapter()

# Check availability
if adapter.available:
    print("Memory system operational")
    if adapter.degraded_mode:
        print("WARNING: Running in degraded mode (no Qdrant)")

# Store a memory
success = await adapter.store_execution_result(
    query="User asked about X",
    result="X is...",
    user_id="user123",
    confidence=0.8
)

# Search memories
results = await adapter.search_memories(
    query="What did we discuss?",
    user_id="user123",
    limit=10
)

# Get all memories
memories = await adapter.get_memories(user_id="user123", limit=100)

# Check if consolidation needed
excess = await adapter.consolidate_if_needed(user_id="user123")
if excess > 0:
    print(f"Should consolidate {excess} memories")
```

## Dependencies

### External Services
- **Qdrant**: Vector database (required for semantic search)
- **Ollama**: LLM for Mem0 consolidation (gemma3:4b)

### Python Packages
- `mem0ai>=1.0.0`: Memory management and consolidation
- `fastembed`: ColBERTv2 embeddings
- `qdrant-client`: Vector database client
- `dspy-ai>=3.1`: Programmatic prompting framework

## Phase 4 Fixes

This architecture document describes the system after Phase 4 fixes:

1. **Fraud #4.3**: Mem0 client now configured with LLM (Ollama gemma3:4b)
2. **Fraud #4.4**: Return key names fixed ("memory" → "content")
3. **Fraud #4.5**: Degraded mode fallback added (no silent failures)
4. **Fraud #3.3**: ColBERT model name externalized to config
5. **Fraud #3.4**: ColBERT vector size externalized to config
6. **Fraud #5.5**: Quality thresholds externalized to config

## Future Enhancements

1. **Hybrid Search**: Combine semantic (ColBERT) with keyword (BM25) search
2. **Fact Expiration**: Time-based invalidation (temporal RAG)
3. **Memory Categories**: Explicit typing (preference, pattern, result)
4. **Cross-User Memories**: Shared knowledge base (with permissions)
5. **Memory Compression**: LLM summarization for old memories

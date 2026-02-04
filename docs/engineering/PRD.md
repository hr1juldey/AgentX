# AGENTX Product Requirements Document (PRD)

**Version:** 1.0
**Date:** 2025-02-04
**Status:** Draft
**Workflow:** PRD → HLD → OpenSpec opsx (LLD) → Implementation

---

## 1. Executive Summary

AGENTX is a **multi-purpose, full-featured AI assistant framework** that combines **DSPy** for all cognitive operations with **LangGraph** for dynamic orchestration. Unlike traditional fixed-pipeline agents, AGENTX uses **self-modifying graphs** that evolve through genetic mutations based on execution history.

**Key Differentiators:**

- DSPy generates graphs, LangGraph executes them
- Pre-compiled graphs mutate to address new situations
- Genetic variations stored for future session optimization
- 6-10 specialized agents with hierarchical routing
- Full voice integration via kyutai voice-server
- 5-tier memory architecture
- Advanced RAG with multi-hop capabilities

---

## 2. Vision and Goals

### 2.1 Primary Vision

Build a **flexible, extensible AI assistant framework** that can:

1. Handle multiple use cases via plugins and specialized agents
2. Adapt its execution graph dynamically based on context
3. Learn from past executions to optimize future performance
4. Support both text and voice interaction modes
5. Operate in hybrid offline/online environments

### 2.2 Success Criteria

- [ ] Dynamic graph mutation produces measurable performance improvements
- [ ] Voice conversation achieves <2s latency from end of speech
- [ ] Multi-hop RAG retrieves relevant information within 3 hops
- [ ] System handles 10+ concurrent agent executions without degradation
- [ ] Plugin system allows external integration without core changes

---

## 3. Core Architecture

### 3.1 Philosophy

```
DSPy = ALL Cognition (agents, tools, reasoning, critics, planners)
LangGraph = ONLY Orchestration (runtime execution, state management)
```

### 3.2 Execution Flow

```
User Query
    ↓
DSPy Planner → JSON Graph Spec
    ↓
Qdrant Retrieval (similar past graphs)
    ↓
Runtime Graph Compiler → LangGraph StateGraph
    ↓
Execution (with streaming)
    ↓
Critic Evaluation
    ↓
Coordinator decides: Continue | Replan | Mutate
    ↓
Successful Graph → Stored in Qdrant (genetic variation)
```

### 3.3 Self-Modifying Graph Execution

The system supports **four mutation operations**:

1. **Add Node**: Inject new agent dynamically
2. **Remove Edge**: Bypass failing path
3. **Modify Condition**: Change routing logic
4. **Spawn Subgraph**: Create isolated subagent execution

Mutation triggers:

- Explicit signal from agent
- Critic score below threshold
- User interruption
- Tool failure (structured error)

---

## 4. Agent Specifications

### 4.1 Agent Categories (6-10 Total)

| Agent | Purpose | Streaming | Memory | Tools |
|-------|---------|-----------|--------|-------|
| **Conversation** | User-facing dialogue | Yes (tokens) | 5-tier | Voice, Subagents |
| **RAG Agent** | Document QA | No | Vector | Retrieve, Cite |
| **Researcher** | Web search + synthesis | No | Session | SearXNG, Parse |
| **Analyst** | Data analysis | No | Session | Code Exec |
| **Designer** | UI generation | No | Context | Templates |
| **Sequencer** | Task orchestration | No | Working | Subagents |
| **Presenter** | Response formatting | No | Context | Formatters |
| **Critic** | Quality evaluation | No | Short-term | Metrics |
| **Planner** | Graph generation | No | Patterns | Registry |
| **Replanner** | Graph mutation | No | History | Qdrant |

### 4.2 Agent Communication

**Typed Contracts with Pydantic Validation:**

- Input/output enforced via Pydantic models at agent boundaries
- On validation failure: Buddy system with hierarchical fallback
  1. Same-signature buddy retries
  2. Complementary buddy fixes + executes
  3. Escalate to Coordinator

**Calling Subagents as Tools:**

- Subagents work independently with isolated state
- Parent agent aggregates results
- Example: Researcher spawns 3 parallel Search subagents

---

## 5. Memory and Retrieval Architecture

### 5.1 Core Principle

**All agents have memory from Mem0AI.** Only agents handling large-scale mixed-quality data (web search, internal dumps) use ColBERTv2 with the **prefetch pattern**.

### 5.2 Memory Tiers

| Tier | Purpose | Technology | Used By |
|------|---------|------------|---------|
| **1. LangGraph State** | Conversation state, checkpointing | SqliteSaver | All agents |
| **2. Mem0AI** | Conversational memory, facts, preferences | Mem0API | **ALL agents** |
| **3. DSPy ReAct** | Step-by-step reasoning traces | DSPy | ReAct agents |
| **4. ColBERTv2** | Large-scale retrieval (prefetch pattern) | Qdrant + Late Interaction | Researcher, MemoryDump only |

### 5.3 Qdrant Collection Architecture

**Two collections** (not three):

```
Qdrant (localhost:6335)
│
├── agentx_memories
│   │ Type: Dense vectors only (384 dims)
│   │ Model: Ollama (nomic-embed-text)
│   │ Purpose: Mem0AI conversational memory (ALL agents)
│   │
│
└── agentx_knowledge
    │ Type: TWO named vectors in ONE collection
    │   ├── dense: BGE-small (384 dims, indexed) → Fast retrieval
    │   └── colbert: ColBERTv2 (N×128 dims, NOT indexed) → Accurate reranking
    │ Purpose: RAG + Research with prefetch pattern
```

**Prefetch Pattern (Qdrant medical bot pattern):**
```
Query → [Dense] → Top 100 candidates (fast, indexed)
         ↓ Prefetch pass
Query → [ColBERTv2] → Rerank → Top 5 results (accurate)
```

### 5.4 Memory Flow

```
User Query
    ↓
LangGraph State (current session checkpoint)
    ↓
Mem0AI.search() → Retrieve relevant context for ALL agents
    ↓
Agent Execution (with Mem0AI context)
    ↓
Result → Mem0AI.add() (store interaction)
    ↓
LangGraph checkpoint updated
```

**For Researcher (web search) and MemoryDump (large-scale) ONLY:**
```
Query → Mem0AI (conversational context)
      → Prefetch pattern: dense (top 100) → ColBERTv2 (rerank top 5)
      → Agent execution
      → Results stored in Qdrant agentx_knowledge for future retrieval
```

### 5.5 Agent Memory Configuration

| Agent | Mem0AI | ColBERTv2 | Notes |
|-------|--------|-----------|-------|
| Conversation | ✅ Yes | ❌ No | Conversational memory only |
| RAG Agent | ✅ Yes | ✅ Yes | Document QA, uses prefetch pattern |
| Researcher | ✅ Yes | ✅ Yes | Web search = mixed quality, needs ColBERTv2 |
| Analyst | ✅ Yes | ❌ No | Data analysis, no large retrieval |
| Designer | ✅ Yes | ❌ No | UI generation |
| Sequencer | ✅ Yes | ❌ No | Task orchestration |
| Presenter | ✅ Yes | ❌ No | Response formatting |
| Critic | ✅ Yes | ❌ No | Quality evaluation |
| Planner | ✅ Yes | ❌ No | Graph generation patterns |
| Replanner | ✅ Yes | ❌ No | Uses Qdrant for graph patterns |
| MemoryDump | ✅ Yes | ✅ Yes | Large-scale internal memory retrieval |

### 5.6 Memory Storage

- **LangGraph**: SQLite with SqliteSaver (conversation checkpoints)
- **Mem0AI**: Persistent storage via Mem0API (conversational memory for all agents)
- **DSPy ReAct**: In-memory during execution (ephemeral reasoning traces)
- **ColBERTv2 + Qdrant**: Large-scale retrieval storage (web search results, internal dumps)
  - Port: 6335 (from docker-compose.yaml)
  - Collection: agentx_knowledge (dense + ColBERTv2 with prefetch)

---

## 6. Component Specifications

### 6.1 DSPy Planner

**Purpose:** Generate JSON graph specifications for query execution

**Input:**

- User query
- Context from memory tiers
- Available agent registry

**Output (Delta/Diff Based):**

```json
{
  "base_graph": "graph_id_or_ref",
  "mutations": [
    {
      "op": "add_node",
      "agent": "researcher.v1",
      "position": "after:analyst"
    },
    {
      "op": "add_conditional_edge",
      "from": "analyst",
      "condition": "needs_info",
      "to": "researcher"
    }
  ],
  "entry_point": "analyst",
  "exit_point": "presenter"
}
```

**Capabilities:**

- Query type classification
- Agent selection from registry
- Flow structure design
- Conditional routing definition

### 6.2 DSPy Critic

**Purpose:** Evaluate agent outputs and trigger replanning

**Input:**

- Agent output
- Expected output format
- Quality criteria

**Output:**

```json
{
  "score": 0.0-1.0,
  "reasoning": "explanation",
  "issues": ["list", "of", "problems"],
  "should_replan": true,
  "suggested_mutation": {...}
}
```

**Evaluation Criteria:**

- Format compliance (Pydantic validation)
- Content relevance
- Completeness
- Accuracy (where verifiable)

### 6.3 Coordinator

**Purpose:** Combine Critic and Planner opinions for replanning decisions

**Responsibilities:**

- Receive signals from any agent
- Gather Critic evaluation
- Consult Planner for mutation options
- Decide: Continue | Replan | Mutate | Escalate
- Execute decision via Graph Compiler

**Decision Logic:**

```
IF Critic.score < threshold OR explicit_signal:
    IF retry_count < max_retries:
        Replan with mutation
    ELSE:
        Escalate to user
ELSE:
    Continue execution
```

### 6.4 Runtime Graph Compiler

**Purpose:** Convert JSON graph specs to executable LangGraph StateGraph

**Input:**

- JSON graph spec (from Planner or Qdrant)
- Agent registry

**Output:**

- Compiled LangGraph StateGraph
- Ready for execution

**Process:**

1. Parse JSON spec
2. Fetch agents from registry
3. Build StateGraph with nodes/edges
4. Apply conditional routing
5. Set entry/exit points
6. Return compiled graph

### 6.5 Agent Registry

**Structure:**

- **Core Agents**: Versioned (agent.v1, agent.v2) in code
- **Plugins**: Auto-register on load via MCP

**Registry Format:**

```python
registry = {
    # Core agents (versioned)
    "conversation.v1": ConversationAgent(),
    "researcher.v2": ResearcherAgent(),
    "critic.v1": CriticAgent(),

    # Plugins (auto-registered)
    "plugin.weather.v1": WeatherPlugin(),
    "plugin.calendar.v1": CalendarPlugin(),
}
```

**Capabilities:**

- Version lookup
- Dependency resolution
- Capability discovery
- Hot-swapping (for trained versions)

---

## 7. Graph Storage and Retrieval

### 7.1 Qdrant Schema

**Stored per graph:**

```json
{
  "graph_id": "uuid",
  "graph_json": "full_graph_spec",
  "embedding": "query_pattern_embedding",
  "metadata": {
    "success_rate": 0.95,
    "avg_latency_ms": 1200,
    "usage_count": 42,
    "last_used": "timestamp",
    "mutation_chain": ["parent_id", "grandparent_id"]
  }
}
```

### 7.2 Graph Retrieval (Two-Stage)

**Stage 1: Planner Request**

- Planner creates query embedding
- Specifies required capabilities

**Stage 2: Retriever Fetch**

- Dedicated GraphRetriever module
- Queries Qdrant for similar patterns
- Returns top N candidates

### 7.3 Warm Cache Strategy

**Startup:**

1. Pre-compile top 10 most-used graphs
2. Load into memory for fast execution

**Runtime:**

- Lazy load mutations on demand
- Cache compiled graphs for reuse
- Evict based on LRU with 100-graph limit

---

## 8. Tool Categories

### 8.1 In-Scope Tools

| Category | Examples | Failure Handling |
|----------|----------|------------------|
| **Code Execution** | Python sandbox, REPL | Wrapper catch → Critic monitor |
| **File Operations** | Read, write, search | Wrapper catch → Critic monitor |
| **Web/API Calls** | HTTP requests, APIs | Wrapper catch → Critic monitor |
| **Communication** | Email, calendar, messaging | Wrapper catch → Critic monitor |
| **Agent Calls** | Subagent spawning | Isolated state → Parent aggregates |
| **Basic Utilities** | Calculator, time, weather | Retry → Buddy → Escalate |

### 8.2 Tool Failure Detection

**Tool Wrapper:**

```python
try:
    result = tool.execute(**kwargs)
    return ToolResult(success=True, data=result)
except Exception as e:
    return ToolResult(
        success=False,
        error=str(e),
        error_type=type(e).__name__
    )
```

**Critic Monitoring:**

- Detects junk patterns (empty results, errors, malformed data)
- Scores output quality
- Triggers replanning if threshold exceeded

### 8.3 Multi-Hop RAG Data Handling

**Problem:** RAG returns too much data

**Solution (Iterative Refine):**

1. Agent detects overflow (>N results or >M tokens)
2. Refines query with more specific terms
3. Re-queries with constraints
4. Iterates until satisfied or max iterations

---

## 9. Voice Integration

### 9.1 Voice Client Library

**Source:** `libs/voice_client/` (reuse directly)

**Capabilities:**

- WebSocket connection to kyutai voice-server
- STT (Speech-to-Text) streaming
- TTS (Text-to-Speech) streaming
- Auto-reconnection with exponential backoff
- JSON and msgpack encoding support

### 9.2 Integration Pattern

**Embedded in Conversation Agent:**

- Conversation agent has voice capability built-in
- Uses voice_client for STT/TTS
- Streams tokens to TTS for real-time response

### 9.3 Audio Flow

```
User Speech → STT Client → Text
    → DSPy Conversation Agent (streaming tokens)
    → TTS Client → Audio Output
```

### 9.4 Voice Specifications

| Property | Value |
|----------|-------|
| Format | 16-bit PCM |
| Sample Rate | 24000 Hz |
| Channels | Mono (1) |
| STT URL | ws://localhost:16000/stt |
| TTS URL | ws://localhost:16000/tts |

---

## 10. Streaming Architecture

### 10.1 Streaming Agents

- **Conversation Agent**: Token streaming (composed streams)
- **Other Agents**: Async/Sync, no streaming

### 10.2 Composed Streams

```
DSPy.streamify(agent) → Agent-level token stream
    → LangGraph StreamWriter → Composed at graph level
    → WebSocket/FastAPI response → Client
```

### 10.3 Stream Types

| Stream | Source | Handler |
|--------|--------|---------|
| Tokens | DSPy LLM | StreamListener |
| Status | StatusMessageProvider | Custom handlers |
| Tool Calls | Agent execution | Logging |
| Errors | Any component | Error handlers |

---

## 11. Retrieval Architecture

### 11.1 Two Retrieval Systems

**IMPORTANT:** AGENTX uses TWO different retrieval systems for different purposes:

| System | Purpose | Used By | Data Characteristics |
|--------|---------|---------|-------------------|
| **DSPy dspy.Retrieve** | Document QA, clean data | RAG Agent | Small, curated, high-quality |
| **Prefetch Pattern (Dense + ColBERTv2)** | Web search, large-scale retrieval | RAG Agent, Researcher, MemoryDump | Large volume, mixed quality |

### 11.2 Qdrant Collection Architecture

**Two collections** (based on Qdrant medical bot pattern):

| Collection | Vectors | Purpose |
|------------|---------|---------|
| `agentx_memories` | dense (384 dims) | Mem0AI conversational memory |
| `agentx_knowledge` | dense (384) + colbert (N×128) | RAG + Research with prefetch reranking |

**Prefetch Pattern (Qdrant medical bot pattern):**
```
Query → [Dense] → Top 100 candidates (fast, indexed)
         ↓ Prefetch pass
Query → [ColBERTv2] → Rerank → Top 5 results (accurate)
```

**Benefits:**
- Dense (indexed, fast) → Initial retrieval
- ColBERTv2 (NOT indexed, accurate) → Final reranking
- One collection → Simpler management

### 11.3 DSPy Retrieve (RAG Agent)

**Purpose:** Document question-answering with clean, curated content.

**Components:**

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Retriever** | DSPy dspy.Retrieve | Query interface |
| **Vector Store** | Qdrant (agentx_knowledge) | Semantic search |
| **Embedding** | Ollama nomic-embed-text | Standard embeddings |
| **Reranker** | DSPy ChainOfThought | Passage refinement |

**Process:**

1. User query about documents
2. DSPy retrieve searches agentx_knowledge collection
3. Uses prefetch pattern: dense (top 100) → ColBERTv2 (rerank top 5)
4. Returns top-k relevant passages
5. Agent synthesizes answer with citations

**Data Characteristics:**
- Clean, structured document content
- Moderate volume (thousands of documents)
- High-quality, curated sources
- Prefetch pattern for optimal speed + accuracy

### 11.4 ColBERTv2 Prefetch (Researcher & MemoryDump)

**Purpose:** Large-scale retrieval for web search results and internal memory dumps.

**Components:**

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Retriever** | Prefetch pattern | Dense → ColBERTv2 reranking |
| **Vector Store** | Qdrant (agentx_knowledge) | Large-scale storage |
| **Embeddings** | BGE-small (dense) + ColBERTv2 (multivector) | Two-stage retrieval |
| **Reranker** | DSPy ChainOfThought | Result refinement |

**Process (Researcher - Web Search):**

1. User query triggers web search via SearXNG
2. SearXNG returns many results (mixed quality)
3. Results stored in agentx_knowledge with BOTH vectors (dense + ColBERTv2)
4. Prefetch pattern: dense retrieves top 100 → ColBERTv2 reranks to top 5
5. Agent synthesizes answer with citations

**Process (MemoryDump - Internal):**

1. Query for internal knowledge
2. Prefetch pattern searches agentx_knowledge
3. Dense (fast) retrieves top 100 → ColBERTv2 (accurate) reranks to top 5
4. Agent uses retrieved context for response

**Data Characteristics:**
- Very large volume (millions of passages)
- Mixed quality (junk, duplicates, noise)
- Prefetch pattern: speed + accuracy
- Needs iterative refinement to handle overflow

### 11.5 Multi-Hop Retrieval (Prefetch Pattern)

**Process:**

1. Initial query → Prefetch pattern retrieves passages
2. Agent identifies gaps or insufficient results
3. Generate follow-up queries with refinement
4. Retrieve additional passages with new queries
5. Synthesize final answer with citations

**Data Management (Iterative Refine):**

- If >N results: Refine query with more specificity
- If >M tokens: Summarize and re-query
- Max iterations: 3
- Detects "junk" patterns and filters out

### 11.6 Qdrant Configuration

**Port:** 6335 (from docker-compose.yaml)

**Collections:**
- `agentx_memories`: Mem0AI conversational memory (dense only)
- `agentx_knowledge`: RAG + Research (dense + ColBERTv2 with prefetch)

---

## 12. Plugin System (FastMCP)

### 12.1 Plugin Architecture

**Core:** FastMCP server for external plugins

**Plugin Types:**

- **Tool Plugins**: Extend tool capabilities
- **Agent Plugins**: Add new agent types
- **DataSource Plugins**: New data sources
- **UI Plugins**: Custom widget types

### 12.2 Plugin Registration

**Auto-Registration:**

```python
# Plugin loads and registers itself
@mcp.tool
def weather_tool(location: str) -> dict:
    """Get weather for location."""
    return weather_api.get(location)

# Registry automatically discovers and indexes
```

**Core vs Plugin:**

- Core agents: Versioned in code base
- Plugins: Auto-register from MCP servers

---

## 13. Performance Requirements (Configurable)

### 13.1 Default SLA

| Metric | Target | Configurable |
|--------|--------|--------------|
| Graph Compile | <100ms | Yes |
| Agent Latency | <200s | Yes |
| Streaming Token | <50ms | Yes |
| Voice RTF | <1.5 | Yes |
| RAG Retrieval | <500ms | Yes |

### 13.2 Performance Configuration

Users can adjust based on use case:

```python
{
    "max_agent_latency": 2.0,  # seconds
    "max_token_latency": 0.05,  # seconds
    "enable_warm_cache": true,
    "cache_size": 100
}
```

---

## 14. Deployment Environment

### 14.1 Cloud Ready

**Architecture supports:**

- Container deployment (Docker)
- Horizontal scaling (stateless agents)
- Cloud storage (Qdrant cloud, managed DBs)
- Load balancing

### 14.2 Local Development

**Supports:**

- Local Ollama for LLM
- Local Qdrant for vector store
- Local voice-server
- SQLite for checkpointing

---

## 15. Monitoring and Observability

### 15.1 Full Observability Stack

**Components:**

- **Logging**: Structured logs (JSON format)
- **Metrics**: Agent latency, success rates, mutation counts
- **Tracing**: OpenTelemetry for request tracing
- **Dashboards**: Real-time system health

### 15.2 Key Metrics

| Metric | Purpose |
|--------|---------|
| Agent latency | Performance monitoring |
| Mutation rate | Graph evolution tracking |
| Critic scores | Quality assessment |
| Cache hit rate | Warm cache effectiveness |
| Tool failures | Reliability monitoring |

---

## 16. Testing Strategy

### 16.1 Full Test Strategy

**Unit Tests:**

- Individual agent modules
- Tool wrappers
- Registry operations

**Integration Tests:**

- Graph compilation
- Multi-agent workflows
- Memory tier interactions

**E2E Tests:**

- Full query flows
- Voice conversations
- Plugin loading

**Performance Tests:**

- Latency benchmarks
- Concurrent execution
- Cache effectiveness

---

## 17. Security (Separate Document)

**Reference:** `docs/engineering/threat_model.md`

**Key Areas:**

- Input validation
- Output sanitization
- Tool execution sandboxing
- API authentication
- Data encryption at rest/transit

---

## 18. Implementation Workflow

```
PRD (this document)
    ↓
HLD (High-Level Design)
    ↓
OpenSpec opsx (LLD generation)
    ↓
Implementation Phases
    ↓
Testing & Deployment
```

---

## 19. Out of Scope (Explicitly Excluded)

| Feature | Reason | Future |
|---------|--------|--------|
| Training Pipeline (GEPA) | Focus on inference | Phase 2 |
| Multi-User Auth | Single-user deployment | Phase 2 |
| Vision/Multimodal | Text+Voice focus | Phase 3 |
| Federation | Single-instance architecture | Phase 3 |
| Rate Limiting | Personal deployment | N/A |
| A/B Testing | Pre-trained agents only | N/A |
| Backup/Restore | Implementation detail | N/A |
| Notifications | Reactive assistant only | Phase 2 |
| I18n | English-only initially | Phase 2 |

---

## 20. Dependencies

### 20.1 External Services

| Service | Purpose | Local Alternative |
|---------|---------|-------------------|
| Ollama | LLM inference | Ollama local |
| Qdrant | Vector storage | Qdrant local |
| Kyutai voice-server | STT/TTS | Local deployment |
| Mem0AI | Long-term memory | Self-hosted |
| SearXNG | Web search | Local instance |

### 20.2 Python Dependencies

```
dspy-ai >= 3.1
langgraph >= 0.2
langchain-core
fastapi
uvicorn
pydantic >= 2.0
qdrant-client
mem0ai
websockets
```

---

## 21. Glossary

| Term | Definition |
|------|------------|
| **DSPy** | Programmatic LLM framework for cognition |
| **LangGraph** | Stateful orchestration framework |
| **Genetic Mutation** | Graph variations stored for optimization |
| **Replanning** | Dynamic graph modification during execution |
| **Buddy Pair** | Fallback agent when primary fails |
| **Typed Contract** | Pydantic-enforced input/output schema |
| **Subagent** | Isolated agent execution within parent graph |
| **Warm Cache** | Pre-compiled graphs in memory |
| **Checkpoint** | Saved state for resume capability |
| **Multi-Hop RAG** | Iterative retrieval with refinement |

---

## 22. Appendix: Research References

Detailed research available in `docs/research/lang__/`:

1. `01_langgraph_core_concepts.md` - StateGraph, nodes, edges
2. `02_deepagents_architecture.md` - Multi-agent patterns
3. `03_ollama_langchain_integration.md` - Ollama configuration
4. `04_async_streaming_patterns.md` - Streaming implementation
5. `05_multiagent_routing.md` - Routing strategies
6. `06_dspy_langgraph_integration.md` - DSPy + LangGraph patterns
7. `07_memory_management.md` - Memory architecture
8. `08_gepa_langgraph_training.md` - Training patterns
9. `09_dspy_ollama_async_streaming.md` - DSPy streaming
10. `10_dspy_retrieve_rag.md` - RAG implementation

---

**Document Status:** Ready for HLD phase
**Next Steps:** Create High-Level Design (HLD.md)

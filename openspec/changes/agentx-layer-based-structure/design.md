# Design: AGENTX Layer-Based Folder Structure

## Context

**Current State:** The `agentx/` directory has minimal organization with no clear architectural boundaries. Code is mixed without clear separation between business logic, application services, infrastructure, and presentation layers.

**Constraints:**
- Must follow `CLAUDE_POLICY.md` (absolute imports only, ruff/pyrefly compliance)
- Must support DSPy stem cell agent architecture with global LM/RM configuration
- Must accommodate LangGraph dynamic routing and graph mutation
- File size limit: 100 lines executable + 50 lines overhead
- Research phase is complete - ready for implementation

**Stakeholders:**
- Developers adding new agents and features
- System maintaining long-term codebase health
- Users expecting consistent API contracts

## Goals / Non-Goals

**Goals:**
- Establish Clean Architecture layering (core, domain, application, infrastructure, presentation)
- Create clear placement rules for all code types (DSPy agents, signatures, tools, graphs, etc.)
- Enable codebase expansion through documented algorithms
- Support LangGraph integration (routing, mutation, storage)
- Enforce absolute imports and file size limits

**Non-Goals:**
- Behavioral changes to existing functionality
- API contract changes (this is purely organizational)
- Dependency additions or removals
- Performance optimizations

## Decisions

### Decision 1: Clean Architecture (5 Layers)

**Choice:** Adopt 5-layer Clean Architecture from mimicus pattern

**Rationale:**
- **core/** - Global singletons and configuration must be centrally accessible
- **domain/** - Business entities should have zero external dependencies (testable, pure)
- **application/** - DSPy agents and graphs orchestrate business logic
- **infrastructure/** - External service clients (Mem0AI, Qdrant, voice) are volatile
- **presentation/** - FastAPI routes and DTOs are the interface boundary

**Alternatives Considered:**
- **3-layer (model/view/controller):** Too flat for DSPy + LangGraph complexity
- **Onion architecture:** Same as Clean Architecture but different naming (prefer explicit layer names)
- **Hexagonal ports-and-adapters:** Over-engineered for our current needs

**Migration:** Create folders first, then move code incrementally

---

### Decision 2: DSPy Global Configuration, Per-Agent Memory

**Choice:** Configure DSPy LM/RM globally in `core/dependencies.py`, inject only Mem0AI per-agent

**Rationale:**
- DSPy's `dspy.configure()` is designed for global LM/RM
- Per-agent LM/RM creates connection overhead and configuration drift
- Mem0AI requires user-scoped memory (must be per-agent)
- Aligns with DSPy best practices from research

```python
# core/dependencies.py
import dspy

def ensure_dspy_configured():
    """Configure DSPy globally with Ollama LM and Qdrant RM."""
    lm = dspy.LM("ollama_chat/gemma3:4b", api_base="http://localhost:11434")
    rm = QdrantRM(...)  # Global retriever
    dspy.configure(lm=lm, rm=rm)

# application/agents/stem_cell.py
class StemCellAgent(dspy.Module):
    def __init__(self, user_id: str, signature: Optional[dspy.Signature] = None):
        # Mem0AI is injected, LM/RM are global
        self.mem0_client = get_mem0_client()
        self.mem0_user_id = user_id
```

**Alternatives Considered:**
- **Per-agent LM/RM:** Rejected - DSPy doesn't support this well, creates overhead
- **All global including Mem0AI:** Rejected - Memory must be user-scoped for privacy

---

### Decision 3: Signature-Based Agent Differentiation

**Choice:** Primary differentiation via DSPy signature changes, not module overexpression

**Rationale:**
- Signature defines input/output contract (the agent's "DNA")
- Simpler than composing multiple modules
- Easier to understand and debug
- Module overexpression still available for advanced cases

```python
# Differentiation pattern
class AnalystAgent(StemCellAgent):
    def __init__(self, user_id: str):
        analyst_signature = dspy.Signature(
            "query, memory_context, knowledge_context -> "
            "context_summary, goals, is_sufficient, confidence"
        )
        super().__init__(user_id=user_id, signature=analyst_signature)
```

**Alternatives Considered:**
- **Module overexpression primary:** Rejected - More complex, harder to debug
- **Separate agent classes (no inheritance):** Rejected - Loses stem cell pluripotency concept

---

### Decision 4: Absolute Imports Only

**Choice:** Enforce absolute imports via `ruff` and manual code review

**Rationale:**
- Required by `CLAUDE_POLICY.md`
- Makes dependencies explicit and traceable
- Prevents circular import issues
- Works better with IDE tooling

```python
# CORRECT
from agentx.domain.entities.graph import Graph
from agentx.application.agents.stem_cell import StemCellAgent

# WRONG
from .graph import Graph
from ..agents.stem_cell import StemCellAgent
```

**Enforcement:**
- `ruff check --fix` auto-fixes most violations
- Manual review for edge cases
- CI/CD gate (future)

---

### Decision 5: File Size Limit with Submodule Splitting

**Choice:** 100 lines executable + 50 lines overhead, split into submodules when exceeded

**Rationale:**
- Forces single-responsibility principle
- Keeps code navigable
- Prevents god objects
- Aligns with mimicus pattern

```python
# When graph_compiler.py exceeds limit, split:
# application/graphs/builder/graph_compiler.py (main compiler)
# application/graphs/builder/node_factory.py (node creation)
# application/graphs/builder/edge_builder.py (edge creation)
```

**Alternatives Considered:**
- **No limit:** Rejected - Leads to unmaintainable files
- **Smaller limit (50 lines):** Rejected - Too restrictive, creates too many files

---

### Decision 6: LangGraph as Application Layer Concern

**Choice:** Place all LangGraph code in `application/graphs/` with subdirectories

**Rationale:**
- LangGraph is an orchestration framework (application concern)
- Builder, routing, mutation, storage are all application-level operations
- Presets are pre-built graph templates (application code)
- Keeps infrastructure layer focused on external services only

```
application/graphs/
├── builder/      # DSPy → LangGraph compilation
├── routing/      # Dynamic routing between graphs
├── mutation/     # Self-modifying graph operations
├── storage/      # Graph persistence (Qdrant wrapper)
└── presets/      # Predefined graph templates
```

**Alternatives Considered:**
- **Put LangGraph in infrastructure/:** Rejected - LangGraph is not an external service
- **Put LangGraph in domain/:** Rejected - LangGraph is orchestration, not pure business logic

---

### Decision 7: Separate Pydantic Models (DSPy vs API)

**Choice:** `application/models/` for internal DSPy models, `presentation/models/` for API DTOs

**Rationale:**
- DSPy models change frequently during optimization
- API models are public contract (should be stable)
- Separation prevents accidental API breakage
- Clearer dependency direction (application → presentation for DTOs only)

```python
# application/models/agent.py (internal)
class AgentConfig(BaseModel):
    signature: str
    enable_tools: bool
    tools: list[str]

# presentation/models/responses.py (API)
class AgentResponse(BaseModel):
    id: str
    status: str
    # Expose only what API consumers need
```

**Alternatives Considered:**
- **Single models/ folder:** Rejected - Unclear which are public vs internal
- **models/ under each layer:** Rejected - Inconsistent with Clean Architecture

---

### Decision 8: Domain-First Development for Expansions

**Choice:** Codebase expansion algorithm starts with domain entities and signatures

**Rationale:**
- Domain entities are stable (no external dependencies)
- DSPy signatures define contracts early (testable without implementation)
- Application layer depends on domain (correct dependency direction)
- Infrastructure depends on domain interfaces (DIP)

**Expansion Flow:**
1. Create domain entity (if needed)
2. Create or reuse DSPy signature
3. Implement agent (application/agents/)
4. Add tools (application/tools/)
5. Add infrastructure clients (if needed)
6. Add API routes (presentation/api/v1/)

**Alternatives Considered:**
- **API-first:** Rejected - Leads to anemic domain model
- **Infrastructure-first:** Rejected - Premature optimization of external concerns

---

### Decision 9: Use Existing voice_client SDK for Kyutai Integration

**Choice:** Use existing `libs/voice_client/` SDK as dependency, wrap with thin adapters in `infrastructure/voice/`

**Rationale:**
- SDK already implements STT/TTS WebSocket protocol with auto-reconnection
- SDK provides VoiceClient, STTClient, TTSClient with proven patterns
- Avoids duplicating complex WebSocket and protocol handling code
- SDK maintains independent versioning and updates

```python
# infrastructure/voice/voice_adapter.py
from voice_client import VoiceClient, ConversationEvent

class VoiceSDKAdapter:
    """Thin wrapper around voice_client SDK for AGENTX integration."""

    def __init__(self, stt_url: str, tts_url: str):
        self.stt_url = stt_url
        self.tts_url = tts_url
        self._client: VoiceClient | None = None

    async def handle_session(self, websocket, session_id: str, agent_callback):
        """Handle voice session using SDK's VoiceClient.converse_stream()."""
        async with VoiceClient(stt_url=self.stt_url, tts_url=self.tts_url) as voice:
            async for event in voice.converse_stream(audio_input, agent_callback):
                # Stream events to WebSocket
                await websocket.send_json({
                    "type": event.type,
                    "data": event.data,
                    "session_id": session_id,
                })
```

**Alternatives Considered:**
- **Implement from scratch:** Rejected - Duplicates 2000+ lines of proven SDK code
- **Copy SDK code into agentx:** Rejected - Loses independent versioning, violates DRY

**Infrastructure Layer Structure:**
```
infrastructure/voice/
├── voice_adapter.py      # VoiceSDKAdapter wrapping voice_client.VoiceClient
├── voice_gateway.py      # VoiceGatewayService for WebSocket endpoint handling
└── text_stream_handler.py # TextStreamHandler for STT buffering/TTS sentence splitting
```

## Risks / Trade-offs

### Risk 1: Migration Breaks Existing Imports

**Risk:** Moving code to new folders breaks all existing imports

**Mitigation:**
- Phase 1: Create new folder structure with empty `__init__.py` files
- Phase 2: Move code incrementally, update imports immediately
- Phase 3: Delete old folders after all code moved
- Run `ruff check --fix` after each move to catch broken imports

---

### Risk 2: Absolute Imports Cause Verbosity

**Risk:** `from agentx.domain.entities.graph import Graph` is verbose

**Mitigation:**
- Accept verbosity as trade-off for explicit dependencies
- Use IDE auto-import to reduce typing
- Clear imports improve code navigation (outweighs verbosity)

---

### Risk 3: File Size Limit Creates Many Small Files

**Risk:** 100-line limit may create too many files to navigate

**Mitigation:**
- Group related files in subdirectories (e.g., `builder/`, `routing/`)
- Use descriptive filenames (`graph_compiler.py`, not `compiler.py`)
- IDE file search handles many files well
- Limit is on executable code only (not total lines)

---

### Risk 4: Clean Architecture Overhead for Simple Features

**Risk:** Adding a simple tool requires multiple folder navigation steps

**Mitigation:**
- Document clear expansion algorithm (copy-paste steps)
- Create CLI scaffolding tool (future enhancement)
- Benefits outweigh costs for codebase of this complexity

---

### Risk 5: LangGraph Mutation Safety

**Risk:** Self-modifying graphs could corrupt running sessions

**Mitigation:**
- Graph mutations create NEW versions, never modify in-place
- Store version history in Qdrant for rollback
- Validate mutations before applying (check for cycles, orphan nodes)
- Run mutations in isolated context before commit

---

### Risk 6: Mem0AI Per-Agent Overhead

**Risk:** Creating Mem0AI client per agent may duplicate connections

**Mitigation:**
- Use singleton Mem0AI client in `core/dependencies.py`
- Pass only `user_id` to agents (not full client)
- Client handles connection pooling internally

```python
# core/dependencies.py
_mem0_client: Optional[MemoryClient] = None

def get_mem0_client() -> MemoryClient:
    global _mem0_client
    if _mem0_client is None:
        _mem0_client = MemoryClient()
    return _mem0_client

# application/agents/stem_cell.py
class StemCellAgent(dspy.Module):
    def __init__(self, user_id: str, ...):
        self.mem0_client = get_mem0_client()  # Singleton
        self.mem0_user_id = user_id  # User-specific
```

## Migration Plan

### Phase 1: Create Folder Skeleton (Non-Breaking)

**Steps:**
1. Create all folders with `__init__.py` files
2. Move `core/config.py` to new structure (update imports)
3. Run `ruff check --fix && ruff format && pyrefly check`

**Rollback:** Delete new folders, restore old files from git

---

### Phase 2: Move Domain Layer (Non-Breaking)

**Steps:**
1. Create `domain/entities/` with Graph, Mutation, Execution entities
2. Create `domain/signatures/` with DSPy signatures
3. Update imports in existing code
4. Run quality checks

**Rollback:** Delete domain folders, restore from git

---

### Phase 3: Move Application Layer (Breaking)

**Steps:**
1. Create `application/agents/` and move `StemCellAgent`
2. Create `application/graphs/` subdirectories
3. Create `application/tools/` and move tools
4. Update all imports in `main.py` and tests
5. Run quality checks

**Rollback:** Delete application folders, restore from git

---

### Phase 4: Move Infrastructure Layer (Breaking)

**Steps:**
1. Create `infrastructure/memory/` and move Mem0AI client
2. Create `infrastructure/voice/` and move voice clients
3. Create `infrastructure/retrieval/` and move RAG clients
4. Update imports in application layer
5. Run quality checks

**Rollback:** Delete infrastructure folders, restore from git

---

### Phase 5: Move Presentation Layer (Breaking)

**Steps:**
1. Create `presentation/api/v1/` subdirectories
2. Move routes from existing structure to new locations
3. Create `presentation/models/` with request/response DTOs
4. Update `main.py` imports
5. Run quality checks

**Rollback:** Delete presentation folders, restore from git

---

### Phase 6: Delete Old Folders

**Steps:**
1. Verify all tests pass
2. Verify all imports are absolute
3. Delete empty old folders
4. Final `ruff check --fix && ruff format && pyrefly check`

**Rollback:** Cannot rollback after deletion (git history available)

## Open Questions

1. **Graph Store Qdrant Collection Naming:** Should graphs be in a separate collection or shared with documents?
   - **Tentative:** Separate collection `agentx_graphs` for different metadata structure

2. **LangGraph Checkpoint Backend:** Redis vs Postgres vs in-memory?
   - **Tentative:** Redis for production (already used elsewhere), in-memory for tests

3. **Stem Cell Agent Signature Validation:** Should signatures be validated at agent init or at compile time?
   - **Tentative:** At agent init (fail fast)

4. **File Size Limit Enforcement:** Manual vs automated (pre-commit hook)?
   - **Tentative:** Manual during migration, add pre-commit hook later

5. **Agent Registry Format:** Dict-based vs class-based for graph compiler?
   - **Tentative:** Dict-based (simpler, matches LangGraph patterns)

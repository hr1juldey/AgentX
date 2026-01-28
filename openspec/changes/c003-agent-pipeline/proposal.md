# Proposal: c003-agent-pipeline

**Generated**: 2026-01-28
**Change**: c003-agent-pipeline
**Schema**: spec-factory v1

---

## Summary

Implement the core agent pipeline using DSPy ReAct agents with conference room orchestration pattern, LangGraph state machines for reasoning flow control, and agentic RAG for memory-aware responses. This enables Real AgentX to process user queries through a multi-stage pipeline: context retrieval → tool selection → reasoning → UI generation → streaming response.

---

## Motivation

### Problem Statement

Real AgentX needs a production-grade agent pipeline that:
- Orchestrates multiple specialist agents (UI, RAG) through a CEO-style coordinator
- Manages complex reasoning flows with state transitions
- Provides real-time streaming of reasoning steps and tool calls
- Integrates memory retrieval with context injection decisions
- Follows locked LLD definitions for entities, signatures, and repositories

### Current State

- **Prototypes exist** (R011, R013, R014) but are scattered and not aligned with LLD
- **Inconsistent patterns** across prototypes (some use streaming, some don't)
- **Missing state machines** - LangGraph planned but not implemented
- **No agent orchestration** - prototypes use single agents, not conference room pattern
- **Memory is basic** - simple context dump, not agentic RAG with quality scoring

### Desired State

- **Aligned with LLD** - All entities, signatures, and repositories match locked definitions
- **Conference Room Pattern** - MainDSPyReActAgent orchestrates UI and RAG specialists
- **LangGraph State Machines** - Backend state (reasoning) + Frontend state (UI lifecycle)
- **Agentic RAG** - Retrieve → Score → Decide → Filter (not simple dump)
- **Streaming First** - All agents support dspy.streamify() with WebSocket delivery

---

## Scope

### In Scope

**DSPy Agents**:
- `MainDSPyReActAgent` (CEO orchestrator with multi-signature pattern)
- `UIDSPyAgent` (UI specialist for descriptor generation)
- `RAGDSPyAgent` (RAG specialist for context retrieval and injection)

**DSPy Signatures**:
- Main signatures: `MainAgentSignature`, `ToolSelectionSignature`, `ConfidenceScoringSignature`
- UI signatures: `SelectWidgetSignature`, `ConfigureFormSignature`, `ShowCardSignature`, `RequestConfirmationSignature`, `UpdateProgressSignature`
- RAG signatures: `RetrievalSignature`, `ContextInjectionSignature`

**DSPy Tools**:
- Main tools: `safe_calculator`, `searxng_search`, `get_current_weather`, `company_mis_search`
- UI tools: `render_markdown_block`, `render_card`, `request_confirmation`, `update_progress`

**LangGraph State Machines**:
- `BackendLangGraphState` with nodes: start, execute_step, complete, error
- `FrontendLangGraphState` with nodes: create, update, dismiss, form_submit, progress

**Application Layer**:
- `ExecuteAgentQueryUseCase` (non-streaming)
- `StreamUIUpdateUseCase` (streaming)
- `AgentOrchestrator` (coordinates state machines + agents)

**API Contracts**:
- REST endpoints: `/api/v1/agent/query`, `/api/v1/agent/stream`, `/api/v1/session/*`
- WebSocket channels: `/ws/agent/{session_id}` with 12 message types
- DTOs: Command/Response patterns with Pydantic → Zod alignment

### Out of Scope

- **Plugin system** - Covered in C006 (Phase 6)
- **Voice streaming** - Covered in C004 (can be developed in parallel)
- **Memory consolidation** - Covered in C005 (extends RAG agent)
- **UI rendering** - Frontend component implementation (separate concern)
- **Advanced optimization** - DSPy MIPROv2 optimizer (future enhancement)

### Dependencies

| Change | Status | Required For |
|--------|--------|--------------|
| **C001-folder-structure** | ✅ Complete | Defines file structure for agent/, application/, infrastructure/ layers |
| **C002-data-contracts** | ✅ Complete | Provides UI descriptors (BaseUIDescriptor, CardDescriptor, etc.) used by UI tools |
| **C004-voice-streaming** | Pending | Independent - can be developed in parallel |
| **C005-memory-rag** | Pending | Extends RAGDSPyAgent with consolidation logic |

---

## Success Criteria

### 1. Agent Pipeline Functional

**Criterion**: MainDSPyReActAgent successfully processes queries with tool use and confidence scoring.

- **Measure**: Integration test passes with calculator tool
- **Target**:
  ```python
  result = agent(user_query="What is 123 * 456?", conversation_history=[], retrieved_context="")
  assert "56088" in result.final_answer
  assert result.confidence_score > 0.7
  assert len(result.tool_calls) > 0
  ```

### 2. Streaming Works End-to-End

**Criterion**: Agent reasoning streams via WebSocket with tokens and steps.

- **Measure**: WebSocket test receives TOKEN, REASONING_STEP, and TOOL_CALL messages
- **Target**: All 3 message types received within 5 seconds of query submission

### 3. Conference Room Orchestration

**Criterion**: CEO agent successfully delegates to UI and RAG specialists.

- **Measure**: Specialist agents called as tools, return correct results
- **Target**: UI specialist returns descriptor ID (not HTML), RAG specialist returns filtered context

### 4. LangGraph State Transitions

**Criterion**: Backend state machine transitions through IDLE → THINKING → USING_TOOL → COMPLETED.

- **Measure**: State machine test follows expected path
- **Target**: All 4 states visited in correct order, no transitions skipped

### 5. Agentic RAG Quality

**Criterion**: RAG agent retrieves, scores, and decides on context injection.

- **Measure**: Context injection decision quality
- **Target**: Correctly injects relevant context, rejects irrelevant context

### 6. LLD Alignment

**Criterion**: 100% alignment with locked LLD definitions.

- **Measure**: grep comparison with LLD documents
- **Target**:
  - All entity fields match: `session_id`, `user_id`, `state`, etc.
  - All enum values match: `INITIALIZING`, `ACTIVE`, `PAUSED`, `CLOSED`
  - All signature fields match: `user_query`, `conversation_history`, `retrieved_context`, etc.

### 7. Code Quality

**Criterion**: All code passes quality checks and file size limits.

- **Measure**: Ruff, pyrefly, file size checks
- **Target**:
  - `ruff check agentx/` - Zero errors
  - `pyrefly check agentx/` - Zero errors
  - No file exceeds 150 lines (100 executable + 50 overhead)

---

## Implementation Approach

### High-Level Approach

**Phase 2: Main DSPy Agent** (from incremental release plan):

1. **Create DSPy signatures** (3 files, ~180 lines)
   - `agent/dspy_signatures/main_signatures.py` - MainAgentSignature, ToolSelectionSignature, ConfidenceScoringSignature
   - `agent/dspy_signatures/ui_signatures.py` - 6 UI signatures
   - `agent/dspy_signatures/rag_signatures.py` - RetrievalSignature, ContextInjectionSignature

2. **Create tools** (2 files, ~180 lines)
   - `agent/tools/main_tools.py` - safe_calculator, searxng_search, get_current_weather
   - `agent/tools/ui_tools.py` - render_markdown_block, render_card, request_confirmation, update_progress

3. **Create agents** (3 files, ~280 lines total)
   - `agent/dspy_agents/main_react_agent.py` - MainDSPyReActAgent (CEO orchestrator)
   - `agent/dspy_agents/ui_agent.py` - UIDSPyAgent (UI specialist)
   - `agent/dspy_agents/rag_agent.py` - RAGDSPyAgent (RAG specialist)

4. **Create use cases** (2 files, ~160 lines)
   - `application/use_cases/execute_agent_query.py` - ExecuteAgentQueryUseCase
   - `application/use_cases/stream_ui_update.py` - StreamUIUpdateUseCase

5. **Create DTOs** (2 files, ~160 lines)
   - `application/dtos/agent_dtos.py` - ExecuteAgentQueryCommand, ExecuteAgentQueryResponse
   - `application/dtos/streaming_dtos.py` - StreamChunk, ReasoningStep, ToolCall

**Phase 4: LangGraph State Machines**:

6. **Create state machines** (2 files, ~300 lines)
   - `agent/langgraph/backend_state_machine.py` - BackendLangGraphState + nodes
   - `agent/langgraph/frontend_state_machine.py` - FrontendLangGraphState + nodes

7. **Create orchestrator** (1 file, ~120 lines)
   - `application/services/agent_orchestrator.py` - Coordinates state machines + agents

### Key Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| **Conference Room Pattern** | Enables specialist agents with clear responsibilities | Single monolithic agent (harder to maintain) |
| **dspy.Tool wrapper required** | Prevents argument hallucination by LLM | Direct function passing (proven to hallucinate) |
| **Sync warmup before async streaming** | Required by DSPy architecture | Skipping warmup (causes errors) |
| **Separate UI/RAG agents** | Separation of concerns, easier testing | All-in-one agent (violates SRP) |
| **LangGraph for state management** | Declarative state machines, visualizable | Manual state tracking (error-prone) |
| **Agentic RAG (not simple dump)** | Better context quality, avoids injection failures | Simple context dump (less reliable) |
| **Port 8015 for API, 8016 for WebSocket** | Avoids conflicts with 8000-8014 range | Port 8000 (reserved for Bytelense) |
| **File split strategy** | Keeps files under 150 lines, improves maintainability | Single large file (violates policy) |

### Constraints

- **Ports**: 8015 (API), 8016 (WebSocket), 8017 (Health) - avoid 8000-8014
- **File size**: Max 100 lines executable + 50 overhead per file
- **Imports**: Absolute only (no `from .` or `from ..`) per CLAUDE_POLICY.md
- **Locked definitions**: Must match LLD exactly (agent_runtime.md, domain_model.md)
- **DSPy version**: Pin `dspy>=3.1.0,<4.0.0` for stability
- **Ollama backend**: Use `ollama_chat/` prefix for LM configuration

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **DSPy API changes** | Low | Medium | Pin `dspy>=3.1.0,<4.0.0` in requirements; monitor releases |
| **Streaming complexity** | Medium | Low | Pattern proven in R013; document warmup requirement explicitly |
| **State machine deadlocks** | Low | High | Add timeout handlers; implement manual state reset endpoint |
| **Tool hallucination** | Low | Medium | Enforce `dspy.Tool()` wrapper in code review; add unit tests |
| **Memory consolidation bugs** | Medium | Medium | Implement comprehensive tests in Phase 5; add rollback logic |
| **Performance degradation** | Low | Medium | Add caching for RAG results; implement request queuing |
| **LangGraph learning curve** | Medium | Low | Follow LLD examples exactly; reference existing tutorials |
| **OOM from streaming** | Low | High | Implement chunk size limits; add memory monitoring |

---

## Open Questions

### 1. Should we implement streaming as SSE or WebSocket?

**Recommendation**: **WebSocket** (per LLD agent_runtime.md:673-750)

**Rationale**:
- WebSocket enables bidirectional communication (needed for form interrupt/resume)
- SSE is unidirectional only
- LLD explicitly specifies WebSocket channels with 12 message types
- Frontend WebSocket support is well-established

**Alternative**: Server-Sent Events (SSE) - simpler but less flexible

### 2. Should we implement all 3 agents (Main, UI, RAG) in Phase 2, or split them?

**Recommendation**: **All 3 agents in Phase 2** (per incremental release plan)

**Rationale**:
- Conference Room Pattern requires all 3 to work together
- UI and RAG agents are relatively simple (~80 lines each)
- Testing the full pipeline early validates the architecture
- Phase 2 is allocated 2-3 hours, sufficient for all 3

**Alternative**: Stagger implementation (Main → UI → RAG) - adds complexity

### 3. Should we implement LangGraph in Phase 2 or Phase 4?

**Recommendation**: **Phase 4** (per incremental release plan)

**Rationale**:
- Agents work without LangGraph (direct forward() calls)
- Phase 2 validates agent logic; Phase 4 adds state machine layer
- Reduces initial complexity
- Follows incremental delivery principle

**Alternative**: Implement LangGraph in Phase 2 - increases upfront complexity

### 4. Should we use Mem0AI directly or wrap it in a MemoryRepository?

**Recommendation**: **Wrap in MemoryRepository** (Clean Architecture)

**Rationale**:
- Enables testing with mock implementations
- Allows swapping Mem0AI for alternative backends
- Follows repository pattern from C001
- LLD defines MemoryRepository ABC (domain_model.md:543-592)

**Alternative**: Use Mem0AI directly - couples domain to infrastructure

### 5. How do we handle session persistence across server restarts?

**Recommendation**: **Redis for active sessions, SQLite for long-term**

**Rationale**:
- Redis: Fast in-memory storage for active sessions
- SQLite: Durable storage for session history
- Matches LLD repository design (RedisSessionAdapter, SQLiteSessionAdapter)
- Follows incremental release plan Phase 1

**Alternative**: Database-only (slower) or memory-only (lost on restart)

---

**Next Artifact**: specs.md

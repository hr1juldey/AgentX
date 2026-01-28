# Tasks Artifact: c003-agent-pipeline

**Generated**: 2026-01-28
**Change**: c003-agent-pipeline
**Schema**: spec-factory v1

---

## 1. Implementation Checklist

### 1.1 Phase 2: Main DSPy Agent (from incremental release plan)

| Task | File | Lines (est.) | Status | Notes |
|------|------|--------------|--------|-------|
| Create MainAgentSignature | `agent/dspy_signatures/main_signatures.py` | 50 | ⬜ | MainAgentSignature, ToolSelectionSignature, ConfidenceScoringSignature |
| Create UI signatures | `agent/dspy_signatures/ui_signatures.py` | 80 | ⬜ | SelectWidgetSignature, ConfigureFormSignature, ShowCardSignature, RequestConfirmationSignature, UpdateProgressSignature |
| Create RAG signatures | `agent/dspy_signatures/rag_signatures.py` | 60 | ⬜ | RetrievalSignature, ContextInjectionSignature |
| Create main tools | `agent/tools/main_tools.py` | 100 | ⬜ | safe_calculator, searxng_search, get_current_weather, company_mis_search |
| Create UI tools | `agent/tools/ui_tools.py` | 80 | ⬜ | render_markdown_block, render_card, request_confirmation, update_progress |
| Create MainDSPyReActAgent | `agent/dspy_agents/main_react_agent.py` | 120 | ⬜ | CEO orchestrator with multi-signature pattern |
| Create UIDSPyAgent | `agent/dspy_agents/ui_agent.py` | 80 | ⬜ | UI specialist for descriptor generation |
| Create RAGDSPyAgent | `agent/dspy_agents/rag_agent.py` | 80 | ⬜ | RAG specialist for context retrieval |
| Create ExecuteAgentQueryUseCase | `application/use_cases/execute_agent_query.py` | 80 | ⬜ | Non-streaming query execution |
| Create StreamUIUpdateUseCase | `application/use_cases/stream_ui_update.py` | 40 | ⬜ | Streaming query execution |
| Create agent DTOs | `application/dtos/agent_dtos.py` | 80 | ⬜ | ExecuteAgentQueryCommand, ExecuteAgentQueryResponse |
| Create streaming DTOs | `application/dtos/streaming_dtos.py` | 60 | ⬜ | StreamChunk, ReasoningStep, ToolCall |
| Create agent routes | `presentation/api/v1/agent_routes.py` | 100 | ⬜ | /api/v1/agent/query, /api/v1/agent/stream |

### 1.2 Phase 4: LangGraph State Machines

| Task | File | Lines (est.) | Status | Notes |
|------|------|--------------|--------|-------|
| Create BackendLangGraphState | `agent/langgraph/backend_state_machine.py` | 150 | ⬜ | Backend state + nodes: start, execute_step, complete, error |
| Create FrontendLangGraphState | `agent/langgraph/frontend_state_machine.py` | 150 | ⬜ | Frontend state + nodes: create, update, dismiss, form_submit, progress |
| Create AgentOrchestrator | `application/services/agent_orchestrator.py` | 120 | ⬜ | Coordinates state machines + agents |
| Create UIService | `application/services/ui_service.py` | 150 | ⬜ | Form interrupt/resume logic |
| Create session routes | `presentation/api/v1/session_routes.py` | 80 | ⬜ | /api/v1/session/* endpoints |

### 1.3 Infrastructure Layer

| Task | File | Lines (est.) | Status | Notes |
|------|------|--------------|--------|-------|
| Create Redis adapter | `infrastructure/database/redis_session_adapter.py` | 80 | ⬜ | RedisSessionAdapter for active sessions |
| Create Qdrant adapter | `infrastructure/database/qdrant_vector_store.py` | 120 | ⬜ | QdrantVectorStoreAdapter for Tier 2 memory |
| Create Mem0AI adapter | `infrastructure/external/mem0_memory.py` | 80 | ⬜ | Mem0MemoryAdapter for Tier 3 memory |
| Create WebSocket manager | `infrastructure/external/websocket_manager.py` | 100 | ⬜ | WebSocketManager for streaming |

### 1.4 Frontend Types

| Task | File | Lines (est.) | Status | Notes |
|------|------|--------------|--------|-------|
| Create agent types | `frontend/types/agent.ts` | 150 | ⬜ | Zod schemas matching Pydantic |
| Create WebSocket types | `frontend/types/websocket.ts` | 100 | ⬜ | Zod schemas for WebSocket messages |

---

## 2. Verification Steps

### 2.1 Code Quality

```bash
# Run all quality checks
cd /home/riju279/Documents/Code/XRIG/AgentX/agentx
ruff check . --fix
ruff format .
pyrefly check . --summarize-errors

# Frontend type check
cd /home/riju279/Documents/Code/XRIG/AgentX/frontend
npx tsc --noEmit
```

### 2.2 File Size Validation

```bash
# Verify no file exceeds 150 lines
find agentx/ -name "*.py" -exec wc -l {} + | awk '$1 > 150 {print FILE TOO LARGE: $2}'
```

### 2.3 Import Validation

```bash
# Verify no relative imports (forbidden by CLAUDE_POLICY.md)
grep -r "from \.\." agentx/  # Should return nothing
grep -r "from \." agentx/ | grep -v "from \.\.\."  # Should return nothing

# Verify absolute imports only
grep -r "^from agentx" agentx/ | head -20  # Should show results
```

### 2.4 LLD Alignment Check

```bash
# Verify MainDSPyReActAgent matches LLD
grep -A 5 "class MainDSPyReActAgent" agentx/agent/dspy_agents/main_react_agent.py
# Should match: agent_runtime.md:368-484

# Verify BackendLangGraphState matches LLD
grep -A 12 "class BackendLangGraphState" agentx/agent/langgraph/backend_state_machine.py
# Should match: agent_runtime.md:681-693

# Verify entity fields match LLD
grep -A 10 "class AgentSessionEntity" agentx/domain/entities/agent_session.py
# Should match: domain_model.md:37-110
```

### 2.5 Tool Wrapping Check

```bash
# Verify all tools wrapped with dspy.Tool
grep "dspy.Tool(" agentx/agent/tools/*.py | wc -l  # Should be > 0

# Verify no direct tool passing
grep "tools=\[" agentx/agent/dspy_agents/*.py | grep -v "dspy.Tool"
# Should return nothing (all tools wrapped)
```

### 2.6 Integration Tests

```bash
# Run integration tests
pytest tests/integration/test_agent_pipeline.py -v

# Run DSPy tests
pytest tests/integration/test_dspy_agents.py -v

# Run state machine tests
pytest tests/integration/test_state_machines.py -v
```

---

## 3. Acceptance Criteria

### 3.1 Functional Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| **Agent processes query with tool use** | Integration test with calculator | `result.final_answer` contains correct answer |
| **Confidence scoring works** | Unit test with mock LLM | `confidence_score` between 0.0 and 1.0 |
| **Streaming works end-to-end** | WebSocket test | Receives TOKEN, REASONING_STEP, TOOL_CALL messages |
| **Conference Room orchestration** | Integration test | UI and RAG specialists called via tools |
| **State machine transitions** | State machine test | IDLE → THINKING → USING_TOOL → COMPLETED |
| **Agentic RAG quality** | RAG test | Context injection decision correct |
| **LLD alignment** | grep comparison | 100% field name match |
| **Tool wrapping** | Code review | All tools wrapped with dspy.Tool |

### 3.2 Non-Functional Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| **Response time** | Benchmark (100 queries) | P95 < 30 seconds for typical queries |
| **Code quality** | `ruff check` | Zero errors |
| **Type checking** | `pyrefly check` | Zero errors |
| **File sizes** | `find + wc` | All files < 150 lines |
| **Import rules** | `grep "from \."` | Zero relative imports |
| **TypeScript compiles** | `npx tsc --noEmit` | Zero errors |

### 3.3 Integration Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| **C001 alignment** | File structure check | Clean Architecture layers match C001 |
| **C002 alignment** | Descriptor usage | UI tools return C002 descriptor IDs |
| **Ollama connection** | `curl http://localhost:11434/api/tags` | Returns model list |
| **Qdrant connection** | `curl http://localhost:6333/` | Returns Qdrant info |
| **Redis connection** | `redis-cli ping` | Returns PONG |

---

## 4. Definition of Done

C003-agent-pipeline is **complete** when:

- [ ] All DSPy signatures created (13 signatures total)
- [ ] All DSPy agents created (Main, UI, RAG)
- [ ] All tools created and wrapped with dspy.Tool
- [ ] LangGraph state machines created and compile
- [ ] All use cases created (ExecuteAgentQuery, StreamUIUpdate)
- [ ] All DTOs created with Pydantic → Zod alignment
- [ ] Frontend Zod schemas match backend Pydantic
- [ ] Zero field name mismatches with LLD
- [ ] Zero relative imports (absolute only)
- [ ] All files under 150 lines
- [ ] All quality checks pass (ruff, pyrefly, tsc)
- [ ] Integration tests pass (agent, RAG, state machines)
- [ ] WebSocket streaming works end-to-end
- [ ] Conference Room pattern validated (specialists called as tools)

---

## 5. Rollback Plan

If implementation fails:

1. **Identify failure point**:
   ```bash
   # Check which test failed
   pytest tests/integration/test_agent_pipeline.py -v
   ```

2. **Rollback steps**:
   ```bash
   # Remove created files
   rm -rf agentx/agent/
   rm -rf agentx/infrastructure/
   rm -rf agentx/application/use_cases/execute_agent_query.py
   rm -rf agentx/application/use_cases/stream_ui_update.py
   rm -rf agentx/presentation/api/v1/agent_routes.py
   rm -rf frontend/types/agent.ts frontend/types/websocket.ts
   ```

3. **Recovery actions**:
   - Re-run from Phase 2 (Main DSPy Agent)
   - Verify each class against LLD before proceeding
   - Run integration tests incrementally (signatures → tools → agents → use cases)

---

## 6. Dependencies Unlocked

This change unlocks:

| Change | Unlocked Feature |
|--------|-----------------|
| **C004-voice-streaming** | Can use agent pipeline for voice interaction (STT → Agent → TTS) |
| **C005-memory-rag** | Can extend RAGDSPyAgent with consolidation logic |
| **C006-release-plan** | Agent pipeline required for full system integration |

---

## 7. Verification Checklist

Before marking C003-agent-pipeline complete, verify:

- [x] All 7 artifacts created (scan, extract, validate, proposal, specs, design, tasks)
- [ ] All implementation tasks in Phase 2 complete
- [ ] All implementation tasks in Phase 4 complete
- [ ] Code quality checks pass
- [ ] LLD alignment verified (grep tests pass)
- [ ] Integration tests pass
- [ ] WebSocket streaming validated

---

**End of spec-factory pipeline**

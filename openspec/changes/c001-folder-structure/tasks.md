# Tasks Artifact: c001-folder-structure

**Generated**: 2026-01-28
**Change**: c001-folder-structure
**Schema**: spec-factory v1

---

## 1. Implementation Checklist

### 1.1 Phase 0: Foundation

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create backend root | `/home/riju279/Documents/Code/XRIG/AgentX/agentx/` | ⬜ | Backend directory |
| Create frontend root | `/home/riju279/Documents/Code/XRIG/AgentX/frontend/` | ⬜ | Frontend directory |
| Create core config | `agentx/core/config.py` | ⬜ | Pydantic Settings (~50 lines) |
| Create dependencies | `agentx/core/dependencies.py` | ⬜ | DI singletons (~30 lines) |
| Create entry point | `agentx/main.py` | ⬜ | FastAPI factory (~20 lines) |
| Create env template | `agentx/.env.example` | ⬜ | Environment variables (~15 lines) |
| Create layer READMEs | `agentx/*/README.md` | ⬜ | Explain each layer's purpose |

### 1.2 Phase 1: Domain + Infrastructure

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create AgentSessionEntity | `agentx/domain/entities/agent_session.py` | ⬜ | @dataclass, ~70 lines |
| Create UIComponentEntity | `agentx/domain/entities/ui_component.py` | ⬜ | @dataclass, ~60 lines |
| Create enums | `agentx/domain/entities/enums.py` | ⬜ | All enums, ~40 lines |
| Create SHA256Hash VO | `agentx/domain/value_objects/sha256_hash.py` | ⬜ | Immutable, ~30 lines |
| Create ToolCall VO | `agentx/domain/value_objects/tool_call.py` | ⬜ | Immutable, ~25 lines |
| Create AgentSessionRepository | `agentx/domain/repositories/agent_session_repository.py` | ⬜ | ABC, ~40 lines |
| Create UIComponentRepository | `agentx/domain/repositories/ui_component_repository.py` | ⬜ | ABC, ~40 lines |
| Create MemoryRepository | `agentx/domain/repositories/memory_repository.py` | ⬜ | ABC, ~50 lines |
| Create RedisSessionAdapter | `agentx/infrastructure/database/redis_session_adapter.py` | ⬜ | Implementation, ~80 lines |
| Create SQLiteSessionAdapter | `agentx/infrastructure/database/sqlite_session_adapter.py` | ⬜ | Implementation, ~90 lines |

### 1.3 Phase 2: Agent Layer

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create main signatures | `agentx/agent/dspy_signatures/main_signatures.py` | ⬜ | MainAgentSignature, ~50 lines |
| Create main tools | `agentx/agent/tools/main_tools.py` | ⬜ | Calculator, search, ~100 lines |
| Create main ReAct agent | `agentx/agent/dspy_agents/main_react_agent.py` | ⬜ | MainDSPyReActAgent, ~120 lines |

### 1.4 Phase 3: UI Layer

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create base descriptor | `agentx/ui/descriptors/base.py` | ⬜ | BaseUIDescriptor, ~40 lines |
| Create markdown descriptor | `agentx/ui/descriptors/markdown_block.py` | ⬜ | MarkdownBlockDescriptor, ~30 lines |
| Create card descriptor | `agentx/ui/descriptors/card.py` | ⬜ | CardDescriptor, ~50 lines |
| Create form descriptor | `agentx/ui/descriptors/form.py` | ⬜ | FormDescriptor, ~100 lines |
| Create progress descriptor | `agentx/ui/descriptors/progress.py` | ⬜ | ProgressDescriptor, ~40 lines |
| Create action descriptor | `agentx/ui/descriptors/action.py` | ⬜ | ActionDescriptor, ~30 lines |
| Create confirmation descriptor | `agentx/ui/descriptors/confirmation.py` | ⬜ | ConfirmationDescriptor, ~50 lines |
| Create voice descriptor | `agentx/ui/descriptors/voice.py` | ⬜ | VoiceDescriptor, ~40 lines |
| Create WebSocket messages | `agentx/ui/protocols/websocket_messages.py` | ⬜ | Message schemas, ~150 lines |

### 1.5 Phase 4: Application Layer

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create use case | `agentx/application/use_cases/execute_agent_query.py` | ⬜ | ExecuteAgentQueryUseCase, ~80 lines |
| Create commands | `agentx/application/commands/agent_commands.py` | ⬜ | Command DTOs, ~30 lines |
| Create queries | `agentx/application/queries/agent_queries.py` | ⬜ | Query DTOs, ~30 lines |
| Create agent DTOs | `agentx/application/dtos/agent_dtos.py` | ⬜ | Pydantic models, ~80 lines |
| Create UI DTOs | `agentx/application/dtos/ui_dtos.py` | ⬜ | Pydantic models, ~60 lines |
| Create agent mapper | `agentx/application/mappers/agent_session_mapper.py` | ⬜ | Static methods, ~40 lines |
| Create UI mapper | `agentx/application/mappers/ui_component_mapper.py` | ⬜ | Static methods, ~40 lines |

### 1.6 Phase 5: Frontend Structure

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create descriptor types | `frontend/types/descriptors.ts` | ⬜ | Zod schemas, ~200 lines |
| Create websocket types | `frontend/types/websocket.ts` | ⬜ | Message types, ~100 lines |
| Create network store | `frontend/store/network-store.ts` | ⬜ | Zustand, ~184 lines |
| Create widget store | `frontend/store/widget-store.ts` | ⬜ | Atomic state, ~312 lines |
| Create UI store | `frontend/store/ui-store.ts` | ⬜ | Zustand, ~100 lines |
| Create useWebSocket hook | `frontend/hooks/useWebSocket.ts` | ⬜ | Custom hook, ~150 lines |

### 1.7 Phase 6: Presentation Layer

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create agent routes | `agentx/presentation/api/v1/agent_routes.py` | ⬜ | REST endpoints, ~100 lines |
| Create health check | `agentx/presentation/api/v1/health.py` | ⬜ | Health endpoint, ~20 lines |

---

## 2. Verification Steps

### 2.1 Code Quality

```bash
# Run all quality checks
cd /home/riju279/Documents/Code/XRIG/AgentX/agentx
ruff check . --fix
ruff format .
pyrefly check . --summarize-errors
```

### 2.2 File Size Check

```bash
# Verify no file exceeds 150 lines
find /home/riju279/Documents/Code/XRIG/AgentX/agentx -name "*.py" -exec wc -l {} + | awk '$1 > 150'
```

### 2.3 Import Check

```bash
# Verify no relative imports
grep -r "from \.\." /home/riju279/Documents/Code/XRIG/AgentX/agentx/  # Should return nothing
grep -r "from \." /home/riju279/Documents/Code/XRIG/AgentX/agentx/ | grep -v "from \.\.\."  # Should return nothing
```

### 2.4 Type Check

```bash
# Frontend type check
cd /home/riju279/Documents/Code/XRIG/AgentX/frontend
npx tsc --noEmit
```

### 2.5 Naming Convention Check

```bash
# Verify no models.py or schemas.py in service folders
find /home/riju279/Documents/Code/XRIG/AgentX/agentx -name "models.py"
find /home/riju279/Documents/Code/XRIG/AgentX/agentx -name "schemas.py"
# Both should return nothing
```

---

## 3. Acceptance Criteria

### 3.1 Functional Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| All 7 backend layers exist | `ls -la agentx/` | core/, domain/, infrastructure/, agent/, ui/, application/, presentation/ present |
| All domain entities are @dataclass | `grep "@dataclass" agentx/domain/entities/*.py` | All entities have decorator |
| All repositories are ABC | `grep "class.*ABC" agentx/domain/repositories/*.py` | All repositories inherit ABC |
| All imports are absolute | `grep -r "from \.\." agentx/` | Zero matches |
| No files exceed 150 lines | `find agentx/ -name "*.py" -exec wc -l {} + | awk '$1 > 150'` | Zero matches |
| Frontend has atomic state | `grep "widget_" frontend/store/widget-store.ts` | Pattern present |
| Zero models.py in services | `find agentx -name "models.py"` | Zero matches |

### 3.2 Non-Functional Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| ruff check passes | `ruff check agentx/` | Zero errors |
| ruff format passes | `ruff format --check agentx/` | Zero changes |
| pyrefly check passes | `pyrefly check agentx/` | Zero errors |
| TypeScript compiles | `npx tsc --noEmit` (in frontend/) | Zero errors |

---

## 4. Definition of Done

C001-folder-structure is **complete** when:

- [x] All 7 backend directories exist with README.md files
- [ ] All domain entities are @dataclass with business methods
- [ ] All repositories follow ABC pattern
- [ ] All imports are absolute paths (zero relative imports)
- [ ] No files exceed 150 lines
- [ ] All code passes ruff check, ruff format, pyrefly check
- [ ] Frontend has atomic state pattern implemented
- [ ] Zero `models.py` or `schemas.py` in service folders
- [ ] All TypeScript files pass `npx tsc --noEmit`

---

## 5. Rollback Plan

If implementation fails:

1. **Identify failure point**: Check which phase/layer failed via verification steps
2. **Rollback steps**:
   ```bash
   # Remove created directories
   rm -rf /home/riju279/Documents/Code/XRIG/AgentX/agentx
   rm -rf /home/riju279/Documents/Code/XRIG/AgentX/frontend
   ```
3. **Recovery actions**:
   - Re-run from Phase 0
   - Verify each phase before proceeding to next
   - Run verification steps after each phase

---

## 6. Dependencies Unlocked

This change unlocks:

| Change | Unlocked Feature |
|--------|-----------------|
| C002-data-contracts | Can define API contracts with folder structure in place |
| C003-agent-pipeline | Can implement DSPy agents with agent/ layer ready |
| C004-voice-streaming | Can implement voice services with infrastructure/ ready |
| C005-memory-rag | Can implement RAG with domain/ repositories ready |
| C006-release-plan | Can execute phases with structure locked |

---

**End of spec-factory pipeline**

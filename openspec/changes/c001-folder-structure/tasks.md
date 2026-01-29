# Tasks Artifact: c001-folder-structure

**Generated**: 2026-01-28
**Change**: c001-folder-structure
**Schema**: spec-factory v1

---

## 1. Implementation Checklist

### 1.0 R014 File Count Reality Check

**R014 Production Files**: 227 Python files
- Services: 192 files (84.6% of codebase)
- API/Presentation: 18 files (7.9%)
- Application: 7 files (3.1%)
- Config/Core: 6 files (2.6%)
- Domain: 4 files (1.8%)
- Models: 1 file (0.4%)
- Entry: 1 file (0.4%)

**AgentX Expected File Count** (conservative estimate):
- Backend: ~180-200 files (C001 + C003 + C004 + C005)
- Frontend: ~40-50 files (C007 + C008 + C009)
- Total: ~220-250 files

**R014 Service Breakdown** (192 files → AgentX mapping):
| Category | R014 Files | AgentX Mapping |
|----------|-----------|----------------|
| Pipeline agents | 31 | `agent/pipeline/*/` (analyst, researcher, etc.) |
| Master agent | 26 | `agent/orchestration/` |
| Widget spawner | 32 | `agent/widget_spawner/` |
| Multihop search | 20 | `agent/multihop_search/` |
| Tools (analyst) | 6 | `agent/pipeline/analyst/tools/` |
| Tools (researcher) | 19 | `agent/pipeline/researcher/tools/` |
| Tools (contextualizer) | 5 | `agent/pipeline/contextualizer/tools/` |
| Tools (designer) | 7 | `agent/pipeline/designer/tools/` |
| Tools (presenter) | 4 | `agent/pipeline/presenter/tools/` |
| Tools (hydrators) | 11 | `agent/tools/hydrators/` |
| Core services | 3 | `agent/tools/common/` |

**Critical**: C001 establishes the folder structure, but actual file creation happens in C003-C005.

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

### 1.3 Phase 2: Agent Layer (Structure Only - Detailed in C003)

**Note**: C001 creates the folder structure. C003 (agent-pipeline) will populate with ~100+ files based on R014.

| Task | File | Status | Notes |
|------|------|--------|-------|
| **LangGraph Core** ||||
| Create graph.py | `agentx/agent/graph.py` | ⬜ | StateGraph definition, ~80 lines |
| Create state.py | `agentx/agent/state.py` | ⬜ | AgentState with ui_message_reducer, ~40 lines |
| Create ui.tsx | `agentx/agent/ui.tsx` | ⬜ | React component registry, ~50 lines |
| **LangGraph Node Layer** (NEW - not in R014) ||||
| Create nodes/ directory | `agentx/agent/nodes/` | ⬜ | 8 node files |
| Create analyst_node | `agentx/agent/nodes/analyst_node.py` | ⬜ | State-aware wrapper, ~60 lines |
| Create researcher_node | `agentx/agent/nodes/researcher_node.py` | ⬜ | State-aware wrapper, ~60 lines |
| Create contextualizer_node | `agentx/agent/nodes/contextualizer_node.py` | ⬜ | State-aware wrapper, ~60 lines |
| Create designer_node | `agentx/agent/nodes/designer_node.py` | ⬜ | STATE AWARE!, ~70 lines |
| Create selector_node | `agentx/agent/nodes/selector_node.py` | ⬜ | Widget selector, ~50 lines |
| Create sequencer_node | `agentx/agent/nodes/sequencer_node.py` | ⬜ | Sequencer, ~50 lines |
| Create presenter_node | `agentx/agent/nodes/presenter_node.py` | ⬜ | Presenter, ~50 lines |
| Create executor_node | `agentx/agent/nodes/executor_node.py` | ⬜ | Tool execution, ~60 lines |
| **Pipeline Directory Structure** (R014 PATTERN) ||||
| Create pipeline/ directory | `agentx/agent/pipeline/` | ⬜ | Domain-centric organization |
| Create analyst/ directory | `agentx/agent/pipeline/analyst/` | ⬜ | 6+ files (C003) |
| Create researcher/ directory | `agentx/agent/pipeline/researcher/` | ⬜ | 19+ files (C003) |
| Create contextualizer/ directory | `agentx/agent/pipeline/contextualizer/` | ⬜ | 5+ files (C003) |
| Create designer/ directory | `agentx/agent/pipeline/designer/` | ⬜ | 7+ files (C003) |
| Create presenter/ directory | `agentx/agent/pipeline/presenter/` | ⬜ | 4+ files (C003) |
| Create sequencer/ directory | `agentx/agent/pipeline/sequencer/` | ⬜ | Files (C003) |
| **Orchestration Directory** (R014 PATTERN: 26 files) ||||
| Create orchestration/ directory | `agentx/agent/orchestration/` | ⬜ | Master agent orchestration |
| **Widget Spawner Directory** (R014 PATTERN: 32 files) ||||
| Create widget_spawner/ directory | `agentx/agent/widget_spawner/` | ⬜ | Multi-agent widget generation |
| **Multihop Search Directory** (R014 PATTERN: 20 files) ||||
| Create multihop_search/ directory | `agentx/agent/multihop_search/` | ⬜ | Reflection-based search |
| **Common Tools Directory** (R014 PATTERN) ||||
| Create tools/common/ directory | `agentx/agent/tools/common/` | ⬜ | type_utils.py, chunking.py |
| Create tools/hydrators/ directory | `agentx/agent/tools/hydrators/` | ⬜ | Data hydration (11 files) |

**Expected Agent/ File Count** (from R014):
- nodes/: 8 files (NEW in AgentX)
- pipeline/: ~50 files (31 agents + ~19 tools)
- orchestration/: 26 files
- widget_spawner/: 32 files
- multihop_search/: 20 files
- tools/: ~14 files (3 common + 11 hydrators)
- **Total**: ~150 files in agent/ layer

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
- [x] All domain entities are @dataclass with business methods
- [x] All repositories follow ABC pattern
- [x] All imports are absolute paths (zero relative imports)
- [x] No files exceed 150 lines
- [ ] All code passes ruff check, ruff format, pyrefly check
- [ ] Frontend has atomic state pattern implemented
- [x] Zero `models.py` or `schemas.py` in service folders
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

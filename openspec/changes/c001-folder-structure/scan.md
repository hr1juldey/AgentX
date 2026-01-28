# Scan Artifact: c001-folder-structure

**Generated**: 2026-01-28
**Change**: c001-folder-structure
**Schema**: spec-factory v1

---

## 1. LLD Synthesis

### 1.1 Relevant LLD Documents

| Document | Path | Relevance |
|----------|------|-----------|
| Incremental Release Plan | `/home/riju279/Documents/Code/XRIG/AgentX/docs/engineering/lld/incremental_release_plan.md` | Phase-by-phase file structure requirements |
| Domain Model | `/home/riju279/Documents/Code/XRIG/AgentX/docs/engineering/lld/domain_model.md` | Entity and repository definitions |
| Agent Runtime | `/home/riju279/Documents/Code/XRIG/AgentX/docs/engineering/lld/agent_runtime.md` | DSPy agent and tool organization |

### 1.2 Locked Definitions from LLD

#### Entities

| Entity | File | Fields |
|--------|------|--------|
| `AgentSessionEntity` | domain_model.md:38-110 | session_id, user_id, state, timestamps, reasoning_step, tool_calls |
| `UIComponentEntity` | domain_model.md:128-187 | component_id, session_id, component_type, state, descriptor, timestamps |
| `MemoryConsolidationEntity` | domain_model.md:202-269 | consolidation_id, session_id, trigger, status, timestamps, results |

#### Enums

| Enum | Values | Location |
|------|--------|----------|
| `SessionState` | INITIALIZING, ACTIVE, PAUSED, CLOSED | domain_model.md:349-356 |
| `UIComponentType` | MARKDOWN, CARD, FORM, PROGRESS, ACTION, CONFIRMATION, VOICE | domain_model.md:358-368 |
| `UIComponentState` | CREATING, CREATED, UPDATING, DISMISSED | domain_model.md:370-377 |
| `ConsolidationTrigger` | SCHEDULED, MANUAL, PRE_QUERY | domain_model.md:379-385 |
| `ConsolidationStatus` | PENDING, IN_PROGRESS, COMPLETED, FAILED | domain_model.md:387-394 |
| `AgentStatus` | IDLE, THINKING, USING_TOOL, COMPLETED, FAILED | domain_model.md:396-404 |
| `VisibilityState` | CHAT_VISIBLE, CHAT_MINIMIZED, CHAT_HIDDEN | domain_model.md:406-412 |

#### Repository Interfaces

| Repository | Methods | Location |
|------------|---------|----------|
| `AgentSessionRepository` | get_by_id, get_by_user_id, get_active_sessions, create, update, delete, exists | domain_model.md:430-470 |
| `UIComponentRepository` | get_by_id, get_by_session_id, get_visible_components, create, update, dismiss, dismiss_by_session, delete | domain_model.md:484-529 |
| `MemoryRepository` | store_memory, search_memories, get_all_memories, update_memory, delete_memory, consolidate_memories | domain_model.md:543-592 |

---

## 2. Codebase Exploration (opsx:explore)

### 2.1 Exploration Topics

```
1. Mimicus Clean Architecture patterns at /home/riju279/Documents/Tools/mimicus/mimicus/src/
2. R014 folder structure and issues at /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/
3. LLD requirements from incremental_release_plan.md
```

### 2.2 File Inventory

#### Backend Files (Mimicus Reference)

| File | Lines | Purpose |
|------|-------|---------|
| `core/config.py` | 53 | Pydantic Settings |
| `core/dependencies.py` | 192 | Dependency injection singletons |
| `core/app.py` | 168 | FastAPI factory |
| `domain/entities/*.py` | 30-80 | @dataclass business entities |
| `domain/repositories/*.py` | 70-85 | ABC interfaces + implementations |
| `application/use_cases/*.py` | 35-80 | Single-purpose classes with execute() |
| `application/dtos/*.py` | 35-120 | Pydantic models for API |
| `application/mappers/*.py` | 25-115 | Entity <-> DTO conversion |
| `presentation/api/v1/*.py` | 65-145 | FastAPI routes |

#### Frontend Files (R014 Reference)

| File | Lines | Purpose |
|------|-------|---------|
| `app/page.tsx` | 464 | Main page (down from 1503!) |
| `components/widgets/*.tsx` | 33-369 | Widget renderers |
| `store/widget-store.ts` | 312 | Atomic state pattern |
| `store/ui-store.ts` | ~100 | UI state management |
| `store/network-store.ts` | 184 | WebSocket/API health |
| `types/widget-types.ts` | 213 | UI descriptor types |

#### R014 Problems (Backend)

| Issue | Location | Impact |
|-------|----------|--------|
| Scattered data models | services/*/schemas.py | Duplication, confusion |
| Hardcoded values | Multiple files | config scattered, not DRY |
| Deprecated files | api/models.py, models/schemas.py | Maintenance burden |
| Too many agents | 21 classes in widget_spawner/ | Complexity explosion |

#### R014 Problems (Frontend)

| Issue | Location | Impact |
|-------|----------|--------|
| Large components | chart-widget.tsx (369 lines) | Should split |
| Large page | page.tsx (464 lines) | Should refactor |

---

## 3. Patterns Discovered

### 3.1 Architectural Patterns

**From Mimicus**:
- Clean Architecture layers: core/ → domain/ → application/ → infrastructure/ → presentation/
- Dependency inversion: domain has no external dependencies
- Repository pattern: ABC interface + implementation(s)
- Use case pattern: single-purpose classes with execute()
- DTO pattern: separate API models from domain entities
- Mapper pattern: static methods for entity ↔ DTO conversion

**From R014**:
- Clean Architecture: domain/ → application/ → api/ (mostly correct)
- Widget streaming: WebSocket for real-time UI updates
- Atomic state pattern: separate Zustand slices prevent cascade re-renders
- Three-tier DSPy: Context Analyzer → Presentation Planner → Enhanced Executor

### 3.2 Code Patterns

**@dataclass Entities** (Mimicus):
```python
@dataclass
class User:
    user_id: str
    username: str
    # ... fields
    def has_role(self, role: str) -> bool:
        return role in self.roles
```

**ABC Repositories** (Mimicus):
```python
class MockRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[MockDefinition]:
        pass
```

**Absolute Imports Only** (Both):
```python
from src.domain.entities.mock_definition import MockDefinition
from config.settings import settings
```

**DTO Pattern** (R014):
```python
class GenerateWidgetRequest(BaseModel):
    query: str
    context: Optional[dict]
```

### 3.3 Anti-Patterns to Avoid

**From R014**:
- ❌ Scattered data models (schemas.py in multiple service folders)
- ❌ Hardcoded URLs/IPs in business logic
- ❌ Deprecated compatibility layers (keep old files around)
- ❌ Too many agent subclasses (use strategy pattern instead)
- ❌ Magic strings in code (use enums)
- ❌ Relative imports (none found in R014, good!)
- ❌ Files > 300 lines for components (split up)

---

## 4. Reference Analysis

### 4.1 Mimicus Patterns (Copy Concepts, Not Names)

| Concept | Mimicus Pattern | Intended Use |
|---------|-----------------|--------------|
| Clean Architecture | core/, domain/, application/, infrastructure/, presentation/ | ✅ Full layer structure |
| Entity | @dataclass with business methods | ✅ AgentSessionEntity, UIComponentEntity |
| Repository | ABC base + implementations | ✅ AgentSessionRepository, MemoryRepository |
| DTO | Pydantic models in application/dtos/ | ✅ Request/Response DTOs |
| Mapper | Static methods in application/mappers/ | ✅ Entity ↔ DTO conversion |
| Use Case | Single-purpose classes with execute() | ✅ ExecuteAgentQueryUseCase |
| DI | Global singletons + getter functions | ✅ get_repository(), get_use_case() |

### 4.2 R014 Reference (Concepts Only)

| Concept | R014 Approach | Improved Approach |
|---------|---------------|-------------------|
| Widget Streaming | WebSocket incremental delivery | ✅ Keep (same pattern) |
| Atomic State | Zustand slices per widget | ✅ Keep (same pattern) |
| Data Models | Scattered schemas.py | ❌ Fix: Consolidate to application/dtos/ |
| Configuration | Hardcoded IPs | ❌ Fix: Single source in config/settings.py |
| Agents | 21 agent classes | ❌ Fix: Strategy pattern with config |
| File Sizes | Up to 369 lines | ❌ Fix: Split > 150 lines |

---

## 5. Key Files for This Change

### LLD Documents (Source of Truth)

```
/home/riju279/Documents/Code/XRIG/AgentX/docs/engineering/lld/incremental_release_plan.md
/home/riju279/Documents/Code/XRIG/AgentX/docs/engineering/lld/domain_model.md
/home/riju279/Documents/Code/XRIG/AgentX/docs/engineering/lld/agent_runtime.md
```

### Mimicus Reference (Clean Architecture)

```
/home/riju279/Documents/Tools/mimicus/mimicus/src/core/config.py
/home/riju279/Documents/Code/XRIG/AgentX/mimicus/src/core/dependencies.py
/home/riju279/Documents/Tools/mimicus/mimicus/src/domain/entities/
/home/riju279/Documents/Tools/mimicus/mimicus/src/domain/repositories/
/home/riju279/Documents/Tools/mimicus/mimicus/src/application/use_cases/
/home/riju279/Documents/Tools/mimicus/mimicus/src/application/dtos/
/home/riju279/Documents/Tools/mimicus/mimicus/src/application/mappers/
/home/riju279/Documents/Tools/mimicus/mimicus/src/presentation/api/v1/
```

### R014 Reference (What to Avoid / Concepts to Keep)

```
/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/domain/entities/ui_descriptor.py
/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/application/dtos/requests.py
/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/frontend/store/widget-store.ts
/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/frontend/types/widget-types.ts
```

### Target Structure (To Create)

```
/home/riju279/Documents/Code/XRIG/AgentX/agentx/                    # Backend root
/home/riju279/Documents/Code/XRIG/AgentX/frontend/                  # Frontend root
```

---

**Next Artifact**: extract.md

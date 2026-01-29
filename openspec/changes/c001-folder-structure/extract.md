# Extract Artifact: c001-folder-structure

**Generated**: 2026-01-28
**Change**: c001-folder-structure
**Schema**: spec-factory v1

---

## 1. Pattern Catalog

### 1.1 Architectural Patterns

| Pattern | Source | Description | Apply? |
|---------|--------|-------------|--------|
| Clean Architecture | mimicus + R014 | Layered separation with domain independence | ✅ |
| Repository Pattern | mimicus + R014 | ABC base + implementations | ✅ |
| DTO Pattern | mimicus + R014 | Pydantic models for API layer | ✅ |
| Use Case Pattern | mimicus + R014 | Single-purpose classes with execute() | ✅ |
| Mapper Pattern | mimicus | Static methods for entity ↔ DTO | ✅ |
| Dependency Injection | mimicus + R014 | Global singletons + getter functions | ✅ |
| LangGraph Node Layer | NEW (LangGraph) | State-aware orchestration layer (fixes R014 duplicate bug) | ✅ |
| Domain-Centric Tools | R014 | Tools organized by pipeline stage (analyst/, researcher/) | ✅ |
| Staggered Delivery | R014 | Progressive widget delivery (2-5s pacing) | ✅ |
| Master Agent Orchestration | R014 | 7-pipeline sequential execution | ✅ |
| Multi-Hop Search | R014 | Reflection-based multi-step search | ✅ |
| Widget Spawner | R014 | Multi-agent widget generation (32 files) | ✅ |

### 1.2 Code Structure Patterns

| Pattern | Example | Apply? |
|---------|---------|--------|
| @dataclass entities | `class AgentSessionEntity:` | ✅ |
| ABC repositories | `class AgentSessionRepository(ABC):` | ✅ |
| Static mappers | `@staticmethod def to_dto()` | ✅ |
| Use case classes | `class ExecuteAgentQueryUseCase:` | ✅ |
| Absolute imports | `from agentx.domain.entities import` | ✅ |
| File size limits | 100 lines executable + 50 overhead | ✅ |
| Single responsibility | One concern per file | ✅ |

### 1.3 Naming Patterns (to Avoid from R014)

| R014 Name | Why Avoid | Alternative |
|-----------|-----------|-------------|
| `models.py` | Scattered across codebase | `domain/entities/*.py` + `application/dtos/*.py` |
| `schemas.py` | Duplicates DTOs | Consolidate to `application/dtos/` |
| `SingleWidgetSpawnerAgent` | Too specific, 21 agent variants | `WidgetAgent` with config |
| `MultiWidgetSpawnerAgent` | Unnecessary subclass | Same agent, different config |
| `WidgetDescriptor` | Redundant suffix | Just `Descriptor` (context implied) |
| `widget_` prefix on everything | Unnecessary repetition | `id`, `type`, `state` (not `widget_id`) |
| Hardcoded IPs | `"192.168.1.4:8080"` in code | Use `config/settings.py` |

### 1.4 R014 Service Organization Patterns (Critical for Migration)

**R014 Service Layer Statistics** (227 production files total, 192 service files = 84.6%):

| Service Category | Files | Description | AgentX Mapping |
|------------------|-------|-------------|----------------|
| **Pipeline Agents** | 31 | Core DSPy agents (analyst, researcher, contextualizer, designer, presenter, sequencer) | `agent/pipeline/*/` |
| **Master Agent** | 26 | Orchestration, delivery planning, QA checkpoints | `agent/orchestration/` |
| **Widget Spawner** | 32 | Multi-agent widget generation system | `agent/widget_spawner/` |
| **Multihop Search** | 20 | Reflection-based multi-step search | `agent/multihop_search/` |
| **Tools (analyst)** | 6 | Query analysis, insight extraction | `agent/pipeline/analyst/tools/` |
| **Tools (researcher)** | 19 | Search, data structuring, citation building | `agent/pipeline/researcher/tools/` |
| **Tools (contextualizer)** | 5 | Data enrichment, filtering | `agent/pipeline/contextualizer/tools/` |
| **Tools (designer)** | 7 | Widget matching, color selection | `agent/pipeline/designer/tools/` |
| **Tools (presenter)** | 4 | Content formatting | `agent/pipeline/presenter/tools/` |
| **Tools (hydrators)** | 11 | Data hydration for widgets | `agent/tools/hydrators/` |
| **Core Services** | 3 | Chunking, decision trees, validation | `agent/tools/common/` |

**R014 Directory Structure** (services/):
```
services/
├── pipeline/              # 31 files - Core DSPy agents
│   ├── analyst.py         # Query analysis (dual-pass pattern)
│   ├── researcher.py      # Web search + beautify
│   ├── data_contextualizer.py  # Rerank → filter → contextualize
│   ├── designer.py        # POV + colors + hierarchy
│   ├── presenter.py       # Final polish + QA
│   └── sequencer.py       # Execution ordering
├── master_agent/          # 26 files - Orchestration
│   ├── master_agent.py    # Main orchestrator (dspy.Module)
│   ├── orchestration/     # Phase execution (11 files)
│   ├── delivery/          # Delivery planning (3 files)
│   └── factory/           # Agent factory (2 files)
├── widget_spawner/        # 32 files - Multi-agent widget generation
├── multihop_search/       # 20 files - Reflection-based search
└── tools/                 # 125 files - Domain-organized utilities
    ├── analyst/           # 6 files
    ├── contextualizer/    # 5 files
    ├── designer/          # 7 files
    ├── presenter/         # 4 files
    ├── researcher/        # 19 files
    └── hydrators/         # 11 files
```

**Key Insight**: R014's proven organization is **domain-centric** - tools are organized by which pipeline stage uses them, not by function.

### 1.5 LangGraph Node Layer Addition

**Critical Architectural Shift**: R014's callback-based pattern → LangGraph's state-based pattern

**R014 Pattern** (Callback-based - NO state awareness):
```python
# R014's master_agent.py
master_agent, delivery_plan_type = use_case.setup_master_agent_with_pipeline(
    widget_callback=send_widget,  # Nested callback - no state awareness!
)
# Problem: Designer agent doesn't know what widgets already exist → duplicates
```

**AgentX Pattern** (State-based - FULL state awareness):
```python
# AgentX's agent/state.py
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    ui: Annotated[Sequence[AnyUIMessage], ui_message_reducer]  # State tracking!
    session_id: str | None
    reasoning_steps: int

# AgentX's nodes/designer_node.py
async def designer_node(state: AgentState):
    existing_widgets = [msg.name for msg in state.get("ui", [])]  # State awareness!
    # Select widget that COMPLEMENTS existing widgets
    push_ui_message(widget_type, widget_props, message=message)
    return {"messages": [message]}
```

**The Node Layer** (`agent/nodes/`):
- NEW in AgentX (not in R014)
- Wraps R014's agent logic with state management
- Each node = LangGraph state transition
- Designer node FIXES R014's duplicate widget bug via `state.ui` awareness

**Hybrid Architecture Decision**:
```
agentx/agent/
├── nodes/                # NEW: LangGraph node layer (state transitions)
│   ├── analyst_node.py          # Wraps analyst agents, checks state
│   ├── researcher_node.py       # Wraps researcher agents, updates state
│   └── designer_node.py         # STATE AWARE: checks state.ui!
│
├── pipeline/             # R014 PATTERN: Domain-centric organization
│   ├── analyst/                 # All analyst modules/tools (6+ files)
│   │   ├── signatures.py
│   │   ├── modules.py
│   │   └── tools/               # query_analyzer, insight_extractor
│   ├── researcher/              # All researcher modules/tools (19+ files)
│   └── designer/                # All designer modules/tools (7+ files)
│
├── orchestration/        # R014's master_agent pattern (26 files)
├── widget_spawner/       # R014 pattern (32 files)
└── multihop_search/      # R014 pattern (20 files)
```

---

## 2. Specification Drafts

### 2.1 Draft: backend-folder-structure Spec

**Purpose**: Define the backend folder structure following Clean Architecture principles from mimicus, with locked entities from LLD.

**Scope**:
- **In scope**: Backend folder structure, layer separation, file organization rules
- **Out of scope**: Frontend structure, runtime behavior, API contracts (covered in other specs)

**Locked from LLD**:
```python
# From domain_model.md:27-110
@dataclass
class AgentSessionEntity:
    session_id: UUID
    user_id: str  # SHA-256 hash
    state: SessionState
    created_at: datetime
    modified_at: datetime
    last_activity_at: datetime
    current_reasoning_step: int = 0
    total_tool_calls: int = 0

@dataclass
class UIComponentEntity:
    component_id: UUID
    session_id: UUID
    component_type: UIComponentType
    state: UIComponentState
    descriptor: BaseUIDescriptor
    created_at: datetime
    updated_at: datetime
    dismissed_at: Optional[datetime] = None
```

**Requirements**:
1. Backend SHALL use Clean Architecture layers: core/, domain/, infrastructure/, agent/, ui/, application/, presentation/
2. Domain entities SHALL use @dataclass with business logic methods
3. Repository interfaces SHALL be ABC in domain/repositories/
4. Repository implementations SHALL be in infrastructure/
5. Application DTOs SHALL be Pydantic v2 models in application/dtos/
6. Use cases SHALL be single-purpose classes in application/use_cases/
7. Mappers SHALL use static methods in application/mappers/
8. All imports SHALL be absolute (no `from .` or `from ..`)
9. No file SHALL exceed 100 lines of executable code + 50 lines overhead

**Acceptance Criteria**:
- [x] All 8 layers exist with correct structure
- [ ] All entities are @dataclass with business methods
- [ ] All repositories follow ABC pattern
- [ ] All imports are absolute paths
- [ ] All files pass `ruff check --fix` and `ruff format`
- [ ] All files pass `pyrefly check --summarize-errors`

---

### 2.2 Draft: frontend-folder-structure Spec

**Purpose**: Define the frontend folder structure following Next.js 15 App Router with atomic state pattern from R014.

**Scope**:
- **In scope**: Frontend folder structure, component organization, state management
- **Out of scope**: Backend structure, WebSocket protocol (covered in other specs)

**Locked from R014 Concepts**:
```typescript
// Atomic state pattern (NOT the names, the concept)
// From R014: store/widget-store.ts
state: {
  widget_abc123_data: UIDescriptor
  widget_abc123_viewState: ViewState
  widget_def456_data: UIDescriptor
  // Separate slices for each widget prevent cascade re-renders
}
```

**Requirements**:
1. Frontend SHALL use Next.js 15 App Router structure
2. Components SHALL be organized in components/ui/ (shadcn), components/descriptors/, components/layout/
3. State SHALL use Zustand with Immer for atomic updates
4. Widget state SHALL use atomic slice pattern (one slice per widget)
5. Types SHALL be defined in types/ directory
6. Hooks SHALL be in hooks/ directory
7. No component SHALL exceed 300 lines (split into sub-components)

**Acceptance Criteria**:
- [ ] All directories exist with correct structure
- [ ] Atomic state pattern implemented for widgets
- [ ] All TypeScript files pass `npx tsc --noEmit`
- [ ] All components < 300 lines

---

### 2.3 Draft: file-naming-conventions Spec

**Purpose**: Define consistent file naming conventions to avoid the scattered model problems in R014.

**Scope**:
- **In scope**: File naming, placement rules, what goes where
- **Out of scope**: Code style, formatting (covered by CLAUDE_POLICY.md)

**Requirements**:
1. Domain entities SHALL be in `domain/entities/<name>.py`
2. Value objects SHALL be in `domain/value_objects/<name>.py`
3. Repository interfaces SHALL be in `domain/repositories/<name>_repository.py`
4. Request DTOs SHALL be in `application/dtos/requests.py` or `application/dtos/<feature>_requests.py`
5. Response DTOs SHALL be in `application/dtos/responses.py` or `application/dtos/<feature>_responses.py`
6. Use cases SHALL be in `application/use_cases/<action>_<entity>.py`
7. Mappers SHALL be in `application/mappers/<entity>_mapper.py`
8. API routes SHALL be in `presentation/api/v1/<feature>_routes.py`
9. NEVER create `models.py` or `schemas.py` in service folders

**Acceptance Criteria**:
- [ ] All files follow naming conventions
- [ ] No `models.py` or `schemas.py` in service folders
- [ ] All data models consolidated to domain/ or application/dtos/

---

## 3. API Contracts

*Note: Folder structure spec does not define API contracts. See C002-data-contracts for API definitions.*

### 3.1 REST Endpoints

None for this spec (structure only, no endpoints defined here)

### 3.2 WebSocket Channels

None for this spec (see C003-agent-pipeline for WebSocket protocol)

### 3.3 Port Assignments

None for this spec (see C004-voice-streaming for port assignments)

---

## 4. Data Model Mappings

### 4.1 File Placement Mappings

| Data Model Type | Backend Location | Frontend Location |
|-----------------|------------------|-------------------|
| Domain entities | `domain/entities/*.py` | N/A (backend only) |
| Value objects | `domain/value_objects/*.py` | N/A |
| Request DTOs | `application/dtos/requests.py` | `types/api-requests.ts` |
| Response DTOs | `application/dtos/responses.py` | `types/api-responses.ts` |
| Shared types | N/A | `types/descriptors.ts` |

### 4.2 Naming Convention Mappings

| Purpose | Backend Pattern | Frontend Pattern |
|---------|-----------------|------------------|
| Entities | `<Name>Entity` | N/A |
| DTOs | `<Name>DTO` | `<Name>Type` |
| Mappers | `<Name>Mapper` | N/A |
| Use Cases | `<Action><Entity>UseCase` | N/A |
| Components | N/A | `<Name>Renderer.tsx` |

---

## 5. Dependencies on Other Specs

| Spec | Dependency Type | Rationale |
|------|-----------------|-----------|
| None | None | C001 is the foundation spec, has no dependencies |

**Unlocks**: C001 enables C002-data-contracts, C003-agent-pipeline, C004-voice-streaming, C005-memory-rag

---

**Next Artifact**: validate.md

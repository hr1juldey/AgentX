# Scan Artifact: dspy-fraud-fix

**Generated**: 2026-02-03
**Change**: dspy-fraud-fix
**Schema**: spec-factory v1.0.0

---

## 1. LLD Synthesis

### 1.1 Relevant LLD Documents

| Document | Path | Relevance |
|----------|------|-----------|
| Domain Model LLD | `docs/engineering/lld/domain_model.md` | Locked entities, enums, repository interfaces |
| DSPy Fraud Analysis | `.claude/fraud/AGENTX_DSPY_FRAUD_ANALYSIS_2026.md` | All 75+ DSPy issues to fix |
| Fix Plan | `.claude/plans/golden-skipping-hedgehog.md` | Implementation plan with batches |

### 1.2 Locked Definitions from LLD

#### Entities (from domain_model.md - LOCKED)

**AgentSessionEntity** - `domain/entities/agent_session.py`
```python
@dataclass
class AgentSessionEntity:
    session_id: UUID
    user_id: str
    state: SessionState
    created_at: datetime
    modified_at: datetime
    last_activity_at: datetime
    current_reasoning_step: int = 0
    total_tool_calls: int = 0
```

**UIComponentEntity** - `domain/entities/ui_component.py`
```python
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

**MemoryConsolidationEntity** - `domain/entities/memory_consolidation.py`
```python
@dataclass
class MemoryConsolidationEntity:
    consolidation_id: UUID
    session_id: UUID
    trigger: ConsolidationTrigger
    status: ConsolidationStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    memories_processed: int = 0
    memories_merged: int = 0
    memories_invalidated: int = 0
```

#### Enums (LOCKED - from domain_model.md)

```python
class SessionState(str, Enum):
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"

class UIComponentType(str, Enum):
    MARKDOWN = "markdown"
    CARD = "card"
    FORM = "form"
    PROGRESS = "progress"
    ACTION = "action"
    CONFIRMATION = "confirmation"
    VOICE = "voice"

class UIComponentState(str, Enum):
    CREATING = "creating"
    CREATED = "created"
    UPDATING = "updating"
    DISMISSED = "dismissed"

class ConsolidationTrigger(str, Enum):
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    PRE_QUERY = "pre_query"

class ConsolidationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentStatus(str, Enum):
    IDLE = "idle"
    THINKING = "thinking"
    USING_TOOL = "using_tool"
    COMPLETED = "completed"
    FAILED = "failed"

class VisibilityState(str, Enum):
    CHAT_VISIBLE = "chat_visible"
    CHAT_MINIMIZED = "chat_minimized"
    CHAT_HIDDEN = "chat_hidden"
```

#### Repository Interfaces (LOCKED - from domain_model.md)

**AgentSessionRepository** - `domain/repositories/agent_session_repository.py`
```python
class AgentSessionRepository(ABC):
    @abstractmethod
    async def get_by_id(self, session_id: UUID) -> Optional[AgentSessionEntity]: pass
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[AgentSessionEntity]: pass
    @abstractmethod
    async def get_active_sessions(self, user_id: str) -> List[AgentSessionEntity]: pass
    @abstractmethod
    async def create(self, session: AgentSessionEntity) -> AgentSessionEntity: pass
    @abstractmethod
    async def update(self, session: AgentSessionEntity) -> AgentSessionEntity: pass
    @abstractmethod
    async def delete(self, session_id: UUID) -> bool: pass
    @abstractmethod
    async def exists(self, session_id: UUID) -> bool: pass
```

**UIComponentRepository** - `domain/repositories/ui_component_repository.py`
```python
class UIComponentRepository(ABC):
    @abstractmethod
    async def get_by_id(self, component_id: UUID) -> Optional[UIComponentEntity]: pass
    @abstractmethod
    async def get_by_session_id(self, session_id: UUID) -> List[UIComponentEntity]: pass
    @abstractmethod
    async def get_visible_components(self, session_id: UUID) -> List[UIComponentEntity]: pass
    @abstractmethod
    async def create(self, component: UIComponentEntity) -> UIComponentEntity: pass
    @abstractmethod
    async def update(self, component: UIComponentEntity) -> UIComponentEntity: pass
    @abstractmethod
    async def dismiss(self, component_id: UUID) -> bool: pass
    @abstractmethod
    async def dismiss_by_session(self, session_id: UUID) -> int: pass
    @abstractmethod
    async def delete(self, component_id: UUID) -> bool: pass
```

**MemoryRepository** - `domain/repositories/memory_repository.py`
```python
class MemoryRepository(ABC):
    @abstractmethod
    async def store_memory(self, content: str, user_id: str, metadata: Optional[Dict[str, Any]] = None) -> UUID: pass
    @abstractmethod
    async def search_memories(self, query: str, user_id: str, limit: int = 10) -> List[Dict[str, Any]]: pass
    @abstractmethod
    async def get_all_memories(self, user_id: str) -> List[Dict[str, Any]]: pass
    @abstractmethod
    async def update_memory(self, memory_id: UUID, new_content: str) -> bool: pass
    @abstractmethod
    async def delete_memory(self, memory_id: UUID) -> bool: pass
    @abstractmethod
    async def consolidate_memories(self, session_id: UUID, user_id: str) -> MemoryConsolidationEntity: pass
```

---

## 2. Codebase Exploration (opsx:explore)

### 2.1 Exploration Topics

```
Forced topics for DSPy fraud fix:
- agentx/agent/dspy_agents/ (all DSPy agents)
- agentx/agent/dspy_signatures/ (all DSPy signatures)
- agentx/agent/tools/ (all 24+ tool modules)
- agentx/infrastructure/memory/ (memory adapters)
- agentx/infrastructure/database/qdrant/ (vector store)
- agentx/core/dependency_facades/dspy.py (DSPy configuration)
- agentx/domain/entities/ (existing entities to extend)
```

### 2.2 File Inventory

#### DSPy Agents
| File | Lines | Purpose |
|------|-------|---------|
| `agentx/agent/dspy_agents/rag_agent.py` | ~140 | RAG specialist (FAKE RAG - Fraud #1) |
| `agentx/agent/dspy_agents/main_react_agent.py` | ~140 | Main ReAct agent with tools |
| `agentx/agent/dspy_agents/agents/main.py` | ~80 | MainDSPyReActAgent |
| `agentx/agent/dspy_agents/agents/analyst.py` | ~50 | AnalystAgent |
| `agentx/agent/dspy_agents/agents/designer.py` | ~50 | DesignerAgent |
| `agentx/agent/dspy_agents/agents/memory.py` | ~40 | MemoryAgent (FAKE memory - Fraud #2) |

#### DSPy Signatures
| File | Lines | Purpose |
|------|-------|---------|
| `agentx/agent/dspy_signatures/` | Multiple | DSPy signature definitions |

#### Tool Modules (24 files with inline signatures + wrong return types)
| File | Lines | Purpose |
|------|-------|---------|
| `agentx/agent/tools/analyst/context_analyzer.py` | ~80 | Query analysis (3 inline sigs) |
| `agentx/agent/tools/analyst/goal_detector.py` | ~60 | Goal detection (3 inline sigs) |
| `agentx/agent/tools/analyst/search_terms.py` | ~50 | Search term extraction |
| `agentx/agent/tools/analyst/insight_extractor.py` | ~70 | Insight extraction |
| `agentx/agent/tools/analyst/data_quality_checker.py` | ~60 | Data quality validation |
| `agentx/agent/tools/researcher/citation_builder.py` | ~70 | Source citation |
| `agentx/agent/tools/researcher/data_structurer.py` | ~80 | Data structuring |
| `agentx/agent/tools/researcher/findings_beautifier.py` | ~70 | Findings formatting |
| `agentx/agent/tools/presenter/quality_check.py` | ~60 | Quality validation |
| `agentx/agent/tools/presenter/presentation.py` | ~80 | Presentation generation |
| `agentx/agent/tools/contextualizer/reranker.py` | ~70 | Relevance ranking (NO filtering - Fraud #5) |
| `agentx/agent/tools/contextualizer/contextualizer.py` | ~60 | Context injection |
| `agentx/agent/tools/contextualizer/filter.py` | ~50 | Context filtering |
| `agentx/agent/tools/designer/color_scheme.py` | ~60 | Color scheme generation |
| `agentx/agent/tools/designer/hierarchy.py` | ~70 | Hierarchy design |
| `agentx/agent/tools/designer/pov_generator.py` | ~60 | POV generation |
| `agentx/agent/tools/main_tools.py` | ~50 | AVAILABLE_TOOLS registry |
| `agentx/agent/tools/planner/query_planner.py` | ~100 | Query planning (EXISTING - must preserve) |

#### Infrastructure
| File | Lines | Purpose |
|------|-------|---------|
| `agentx/infrastructure/memory/mem0_adapter.py` | ~150 | Mem0 integration |
| `agentx/infrastructure/database/qdrant/qdrant_vector_store.py` | ~200 | Qdrant vector store with ColBERTEmbedder |
| `agentx/infrastructure/database/qdrant/embedding_service.py` | ~50 | ColBERTEmbedder (colbert-ir/colbertv2.0) |
| `agentx/core/dependency_facades/dspy.py` | ~50 | DSPy configuration (cache=False - Fraud #53) |

#### Domain Entities (extend these)
| File | Lines | Purpose |
|------|-------|---------|
| `agentx/domain/entities/enums.py` | ~50 | Existing enums (extend with new types) |
| `agentx/domain/entities/agent_session.py` | ~110 | AgentSessionEntity |
| `agentx/domain/entities/ui_component.py` | ~90 | UIComponentEntity |
| `agentx/domain/entities/memory_consolidation.py` | ~70 | MemoryConsolidationEntity |

#### Graph Architecture
| File | Lines | Purpose |
|------|-------|---------|
| `agentx/agent/graph/dynamic_agent_graph.py` | ~150 | LangGraph compilation (EXISTING) |
| `agentx/agent/nodes/` | Multiple | Graph nodes (query_planner, cache_lookup, etc.) |

#### Frontend
| File | Lines | Purpose |
|------|-------|---------|
| `frontend/` | Multiple | Next.js frontend (out of scope for DSPy fixes) |

---

## 3. Patterns Discovered

### 3.1 Architectural Patterns

**Clean Architecture (4-layer)**:
- `domain/` - Entities, repositories (ABC), value objects, services
- `application/` - Use cases, DTOs, mappers
- `infrastructure/` - External implementations (Qdrant, Mem0, HTTP)
- `presentation/` - FastAPI routes, WebSocket

**LangGraph Pattern**:
- `StateGraph` with nodes and conditional edges
- Dynamic workers via `Send` API
- Checkpointer (graph memory) + Store (agent memory)
- Lazy graph compilation

**DSPy Pattern**:
- `dspy.Module` base class for all agents
- `dspy.Signature` for input/output contracts
- `dspy.Predict()` for single-step operations
- `dspy.ReAct()` for multi-step reasoning with tools
- `dspy.Prediction` return type (NOT dict)

### 3.2 Code Patterns

**Entity Pattern**:
```python
@dataclass
class Entity:
    # Identity fields
    id: UUID

    # State fields
    state: Enum
    created_at: datetime

    # Business methods
    def method(self) -> None:
        pass
```

**Repository Pattern**:
```python
class Repository(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[Entity]: pass

    @abstractmethod
    async def create(self, entity: Entity) -> Entity: pass
```

**DSPy Module Pattern** (CORRECT):
```python
class MyModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(MySignature)  # Class-based signature

    def forward(self, input: str) -> dspy.Prediction:  # NOT dict
        result = self.predict(input=input)
        return dspy.Prediction(output=result.output)
```

### 3.3 Anti-Patterns Found (from Fraud Analysis)

**Fraud #1: Fake RAG** - `rag_agent.py` uses `dspy.Predict` instead of `dspy.Retrieve`

**Fraud #2: Fake Memory** - `agents/memory.py` uses `dspy.Predict` instead of real Mem0 access

**Fraud #5: Ignored Quality Scores** - `reranker.py` computes scores but doesn't filter

**Fraud #6-17: Inline Signatures** - 12 violations across tool files (weak LLM incompatible)

**Fraud #18-41: Wrong Return Types** - 24 modules return `dict` instead of `dspy.Prediction`

**Fraud #53: DSPy Cache Disabled** - `dspy.py` has `cache=False`

---

## 4. Reference Analysis

### 4.1 Mimicus Patterns (Copy Concepts, Not Names)

| Concept | Mimicus Pattern | Intended Use |
|---------|-----------------|--------------|
| Clean Architecture | `core/`, `domain/`, `application/`, `infrastructure/`, `presentation/` | Layered separation |
| Repository | ABC base class + implementations in infrastructure | Data access abstraction |
| Entity | `@dataclass` with business methods | Domain model with behavior |
| Use Case | Single-purpose classes with `execute()` method | Application logic orchestration |
| DTO | Pydantic models in `application/dtos/` | API layer data transfer |

### 4.2 R014 Reference (Concepts Only)

| Concept | R014 Approach | Improved Approach |
|---------|---------------|-------------------|
| DSPy Retrieval | Fake (uses `dspy.Predict`) | Real (use Mem0 wrapper) |
| Memory Storage | Direct Qdrant | Via Mem0AI adapter |
| Search Integration | SearXNG via tools | Preserved (enhance with memory guidance) |
| Graph Routing | Fixed agent sequence | Dynamic routing based on session performance |

---

## 5. Key Files for This Change

### NEW Files to Create

**Phase 0: Foundation**
```
/home/riju279/Documents/Code/XRIG/AgentX/agentx/domain/entities/memory_record.py
/home/riju279/Documents/Code/XRIG/AgentX/agentx/domain/entities/session_performance.py
/home/riju279/Documents/Code/XRIG/AgentX/agentx/application/services/routing_decision_service.py
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/nodes/routing_performance.py
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/dspy_signatures/decision_signatures.py
/home/riju279/Documents/Code/XRIG/AgentX/agentx/infrastructure/retrieval/mem0_dspy_retriever.py
/home/riju279/Documents/Code/XRIG/AgentX/agentx/infrastructure/memory/context_rot_manager.py
/home/riju279/Documents/Code/XRIG/AgentX/agentx/infrastructure/memory/reinforcement_tracker.py
```

**Phase 1: Content Quality**
```
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/dspy_signatures/synthesis_signatures.py
/home/riju279/Documents/Code/XRIG/AgentX/agentx/application/services/synthesis_service.py
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/tools/memory_tools.py
```

**Phase 2: Anti-Patterns**
```
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/dspy_signatures/analyst.py
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/dspy_signatures/researcher.py
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/dspy_signatures/presenter.py
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/dspy_signatures/designer.py
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/dspy_signatures/contextualizer.py
```

### Files to MODIFY

```
/home/riju279/Documents/Code/XRIG/AgentX/agentx/domain/entities/enums.py (extend)
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/nodes/query_planner.py (ENHANCE, not replace)
/home/riju279/Documents/Code/XRIG/AgentX/agentx/infrastructure/memory/mem0_adapter.py (update)
/home/riju279/Documents/Code/XRIG/AgentX/agentx/core/dependency_facades/dspy.py (enable cache)
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/dspy_agents/rag_agent.py (real RAG)
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/dspy_agents/agents/main.py (Mem0 integration)
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/dspy_agents/agents/analyst.py (Mem0 integration)
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/dspy_agents/agents/designer.py (Mem0 integration)
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/tools/main_tools.py (add memory tools)
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/tools/contextualizer/reranker.py (add filtering)
```

### Files to DELETE

```
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/agents/widget_matcher.py (dead code)
```

### CRITICAL: Existing Files to PRESERVE

```
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/graph/dynamic_agent_graph.py (LangGraph compilation)
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/nodes/query_planner.py (ExecutionPlan generation)
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/nodes/cache_lookup.py (cache checking)
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/tools/researcher/search_executor.py (SearXNG integration)
/home/riju279/Documents/Code/XRIG/AgentX/agentx/domain/models/graph_state.py (AgentState structure)
```

---

**Next Artifact**: extract.md

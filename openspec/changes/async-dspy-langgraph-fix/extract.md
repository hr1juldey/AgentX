# Extract Artifact: async-dspy-langgraph-fix

**Generated**: 2026-02-01
**Change**: async-dspy-langgraph-fix
**Schema**: spec-factory v1.0.0

---

## 1. Pattern Catalog

### 1.1 Architectural Patterns

| Pattern | Source | Description | Apply? |
|---------|--------|-------------|--------|
| Clean Architecture | mimicus | Layered separation with domain independence | ✅ Existing |
| Repository Pattern | mimicus | ABC base + implementations | ✅ Existing |
| DTO Pattern | mimicus | Pydantic models for API layer | ✅ Existing |
| DSPy Module Pattern | DSPy docs | `forward()` + `aforward()` for sync/async variants | ✅ NEW |
| LangGraph State Reducers | LangGraph docs | `Annotated[list, operator.add]` for parallel writes | ✅ NEW |
| LangGraph Parallel Nodes | LangGraph docs | Multiple START edges for concurrent execution | ✅ NEW |
| asyncio.gather() Batching | DSPy docs + test findings | Batch independent calls within nodes | ✅ NEW |
| Model Pre-warming | Test findings | 3-5 warmup queries before production use | ✅ NEW |

### 1.2 Code Structure Patterns

| Pattern | Example | Apply? |
|---------|---------|--------|
| @dataclass entities | `class AgentSessionEntity:` | ✅ Existing |
| ABC repositories | `class AgentSessionRepository(ABC):` | ✅ Existing |
| Static mappers | `@staticmethod def to_dto()` | ✅ Existing |
| Use case classes | `class CreateSessionUseCase:` | ✅ Existing |
| DSPy Signature classes | `class QueryAnalysisSignature(dspy.Signature):` | ✅ NEW (replace string signatures) |
| DSPy Module with aforward() | `async def aforward(self, ...)` | ✅ NEW (mirror forward()) |
| LangGraph async nodes | `async def my_node(state: State):` | ✅ NEW |
| Configuration-based batching | `settings.dspy_async_batch_size: int = 4` | ✅ NEW |

### 1.3 Naming Patterns (to Avoid from R014)

| R014 Name | Why Avoid | Alternative |
|-----------|-----------|-------------|
| String signatures | `dspy.Predict("query->query_type")` - causes Pydantic warnings | Proper Signature class with typed fields |
| Complex instructions | "high effort" prompts perform worse | Simple, direct queries (test finding) |
| Stiff behavior | R014 uses "stiff behavior" | More natural prompts with simpler instructions |

### 1.4 Anti-Patterns Discovered

| Anti-Pattern | Problem | Target Pattern |
|--------------|---------|----------------|
| Sequential DSPy calls in async nodes | Blocks event loop, ~24-32s per pass | `asyncio.gather()` for independent calls |
| No model pre-warming | Cold start ~8s per query, ~27s warmup | Startup pre-warming service |
| Complex query instructions | Test shows simple queries faster | `DSPY_USE_SIMPLE_QUERIES=True` |
| String signatures | Pydantic warnings, no type safety | Proper Signature classes |
| >4 concurrent calls | Test shows diminishing returns | `DSPY_ASYNC_BATCH_SIZE=4` max |

---

## 2. Specification Drafts

### 2.1 Draft: DSPy Performance Optimization Spec

**Purpose**: Define performance optimization patterns for DSPy + LangGraph integration to prevent 60s timeout

**Scope**:
- **In scope**: DSPy async batching, model pre-warming, LangGraph node optimization, configuration settings
- **Out of scope**: Frontend changes, API contract changes, database schema changes

**Locked from LLD**:
```python
# From Domain Model LLD
class AgentSessionEntity:
    session_id: UUID
    user_id: str  # SHA-256 hash
    state: SessionState
    current_reasoning_step: int
    total_tool_calls: int

# SessionState enum values
INITIALIZING = "INITIALIZING"
ACTIVE = "ACTIVE"
PAUSED = "PAUSED"
CLOSED = "CLOSED"
```

**Requirements**:

1. **DSPy Async Batching**
   - All 16 DSPy tool modules must implement `aforward()` method mirroring `forward()`
   - LangGraph nodes must batch independent DSPy calls using `asyncio.gather()`
   - Maximum batch size: 4 concurrent calls (test-validated optimal)

2. **Model Pre-warming**
   - Service must execute 3-5 warmup queries at startup
   - Pre-warming must complete before accepting user requests
   - Must log duration for each warmup query

3. **Configuration**
   - `DSPY_PREWARM_ENABLED`: Enable/disable pre-warming (default: True)
   - `DSPY_PREWARM_QUERIES`: Number of warmup queries (default: 5)
   - `DSPY_ASYNC_BATCH_SIZE`: Max concurrent async calls (default: 4)
   - `DSPY_USE_SIMPLE_QUERIES`: Use simple prompt templates (default: True)

4. **DSPy Signature Fixes**
   - Replace all string signatures (`"query->answer"`) with proper Signature classes
   - Use `dspy.InputField()` and `dspy.OutputField()` with descriptions

5. **Performance Target**
   - Current: 60s+ (timeout)
   - Target: ~20-25s (safe margin under 60s)
   - Method: Pre-warm ~27s one-time, then ~2s per query with 4x batching

**Acceptance Criteria**:
- [ ] All 16 DSPy tools have `aforward()` methods implemented
- [ ] analyst.py Pass 1 uses `asyncio.gather()` for independent calls (2 parallel, 2 sequential)
- [ ] researcher.py batches independent calls with `asyncio.gather()`
- [ ] designer.py batches independent calls with `asyncio.gather()`
- [ ] Pre-warming service executes 5 warmup queries at startup
- [ ] All string signatures replaced with proper Signature classes
- [ ] Configuration settings added to `agentx/core/config.py`
- [ ] End-to-end execution completes in <60s consistently
- [ ] Ruff and pyrefly checks pass for all modified files

**Dependencies**:
- Requires: Domain Model LLD (AgentSessionEntity)
- Requires: Agent Runtime LLD (DSPy signatures, LangGraph state machines)

---

## 3. API Contracts

### 3.1 REST Endpoints

| Method | Path | Request | Response |
|--------|------|---------|----------|
| (None - this change is internal only) | | | |

**Note**: This change modifies internal behavior only. No REST API changes.

### 3.2 WebSocket Channels

| Channel | Message Type | Schema |
|---------|--------------|--------|
| (None - this change is internal only) | | |

**Note**: This change modifies internal behavior only. No WebSocket changes.

### 3.3 Port Assignments

| Service | Port | Purpose |
|---------|------|---------|
| (No new services - uses existing backend port) | | |

**Note**: This change uses existing backend infrastructure. No new ports required.

---

## 4. Data Model Mappings

### 4.1 Pydantic → Zod Mappings

| Pydantic Model | Zod Type | Notes |
|----------------|----------|-------|
| `AnalysisResult` | `AnalysisResultSchema` | Analyst node output |
| `ResearchResult` | `ResearchResultSchema` | Researcher node output |
| `UIDesignResult` | `UIDesignResultSchema` | Designer node output |
| `ContextQuery` | `ContextQuerySchema` | Contextualizer input |
| `PrewarmStatus` | `PrewarmStatusSchema` | Pre-warming service status |

**Note**: Even though this is a backend optimization, defining these models ensures inter-agent data consistency and enables proper error propagation to frontend.

### 4.2 Shared Types

```python
# Backend (Pydantic v2)
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class QueryType(str, Enum):
    FACTUAL = "factual"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    PROCEDURAL = "procedural"

class AnalysisResult(BaseModel):
    """Output from analyst node Pass 1 - context analysis."""
    query_type: QueryType = Field(description="Type of query classified")
    domain: str = Field(description="Domain of the query (e.g., science, history)")
    urgency: str = Field(description="Urgency level: low/medium/high")
    insights: list[str] = Field(default_factory=list, description="Key insights extracted")

class GoalAnalysis(BaseModel):
    """Output from analyst node - goal detection."""
    primary_goal: str = Field(description="Primary user goal")
    sub_goals: list[str] = Field(default_factory=list, description="Sub-goals identified")

class SearchTermsResult(BaseModel):
    """Output from analyst node - search term extraction."""
    terms: list[str] = Field(description="Search terms for research")
    filters: dict[str, str] = Field(default_factory=dict, description="Metadata filters")

class ResearchResult(BaseModel):
    """Output from researcher node."""
    sources: list[str] = Field(description="Source URLs/references")
    findings: str = Field(description="Structured research findings")
    citations: list[str] = Field(default_factory=list, description="Citation strings")

class UIDesignResult(BaseModel):
    """Output from designer node."""
    widget_type: str = Field(description="UI widget component name")
    color_scheme: dict[str, str] = Field(default_factory=dict, description="Color palette")
    hierarchy_level: int = Field(description="Visual hierarchy (1-5)")
    accessibility_notes: list[str] = Field(default_factory=list)

class ContextQuery(BaseModel):
    """Input for contextualizer node."""
    query: str = Field(description="User query")
    context_type: str = Field(description="Type of context needed")
    max_results: int = Field(default=5, description="Max context items to retrieve")

class PrewarmStatus(BaseModel):
    """Status of DSPy model pre-warming."""
    is_prewarmed: bool = Field(description="Whether pre-warming completed")
    queries_executed: int = Field(description="Number of warmup queries run")
    total_duration_ms: float = Field(description="Total pre-warming duration")
    per_query_ms: list[float] = Field(default_factory=list, description="Duration per query")
```

```typescript
// Frontend (Zod)
import { z } from "zod";

// Enums
const QueryTypeSchema = z.enum(["factual", "analytical", "creative", "procedural"]);

// Analysis result from analyst node
export const AnalysisResultSchema = z.object({
  query_type: QueryTypeSchema,
  domain: z.string(),
  urgency: z.string(),
  insights: z.array(z.string()).default([]),
});

export type AnalysisResult = z.infer<typeof AnalysisResultSchema>;

// Goal analysis from analyst node
export const GoalAnalysisSchema = z.object({
  primary_goal: z.string(),
  sub_goals: z.array(z.string()).default([]),
});

export type GoalAnalysis = z.infer<typeof GoalAnalysisSchema>;

// Search terms from analyst node
export const SearchTermsResultSchema = z.object({
  terms: z.array(z.string()),
  filters: z.record(z.string()).default({}),
});

export type SearchTermsResult = z.infer<typeof SearchTermsResultSchema>;

// Research result from researcher node
export const ResearchResultSchema = z.object({
  sources: z.array(z.string()),
  findings: z.string(),
  citations: z.array(z.string()).default([]),
});

export type ResearchResult = z.infer<typeof ResearchResultSchema>;

// UI design result from designer node
export const UIDesignResultSchema = z.object({
  widget_type: z.string(),
  color_scheme: z.record(z.string()).default({}),
  hierarchy_level: z.number().int().min(1).max(5),
  accessibility_notes: z.array(z.string()).default([]),
});

export type UIDesignResult = z.infer<typeof UIDesignResultSchema>;

// Context query for contextualizer
export const ContextQuerySchema = z.object({
  query: z.string(),
  context_type: z.string(),
  max_results: z.number().int().default(5),
});

export type ContextQuery = z.infer<typeof ContextQuerySchema>;

// Pre-warming status (for health check endpoints)
export const PrewarmStatusSchema = z.object({
  is_prewarmed: z.boolean(),
  queries_executed: z.number().int(),
  total_duration_ms: z.number(),
  per_query_ms: z.array(z.number()),
});

export type PrewarmStatus = z.infer<typeof PrewarmStatusSchema>;
```

### 4.3 Data Flow Diagram

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ LangGraph State (TypedDict)                                 │
│ - query: str                                                │
│ - analysis: Optional[AnalysisResult]  ← Pydantic model      │
│ - goals: Optional[GoalAnalysis]        ← Pydantic model      │
│ - search_terms: Optional[SearchTermsResult] ← Pydantic      │
│ - research: Optional[ResearchResult]    ← Pydantic model      │
│ - ui_design: Optional[UIDesignResult]   ← Pydantic model      │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Analyst Node (Pass 1)                                       │
│ ┌─────────────────┐  ┌─────────────────┐                   │
│ │ ContextAnalyzer │  │ InsightExtractor│  ← Parallel via   │
│ │ → AnalysisResult│  │ → list[str]     │    asyncio.gather │
│ └─────────────────┘  └─────────────────┘                   │
│         │                           │                       │
│         └───────────┬───────────────┘                       │
│                     ▼                                       │
│              GoalDetector (depends on insights)             │
│              SearchTermsExtractor (depends on domain)       │
└─────────────────────────────────────────────────────────────┘
```

### 4.4 Dependency Injection Pattern

```python
# domain/services/analyst_service.py
from pydantic import BaseModel
from typing import Protocol

class IAnalystService(Protocol):
    """Protocol for analyst service - enables DI testing."""
    async def analyze_query(self, query: str) -> AnalysisResult: ...
    async def detect_goals(self, query: str, insights: list[str]) -> GoalAnalysis: ...
    async def extract_search_terms(
        self, query: str, insights: list[str], domain: str
    ) -> SearchTermsResult: ...

# application/use_cases/analyze_query.py
class AnalyzeQueryUseCase:
    """Use case with DI for analyst operations."""

    def __init__(self, analyst_service: IAnalystService):
        self._analyst_service = analyst_service

    async def execute(self, query: str) -> dict[str, BaseModel]:
        """Returns dict of Pydantic models - not raw dicts."""
        analysis, insights = await asyncio.gather(
            self._analyst_service.analyze_query(query),
            self._analyst_service.extract_insights(query),
        )
        goals = await self._analyst_service.detect_goals(query, insights.insights)
        terms = await self._analyst_service.extract_search_terms(
            query, insights.insights, analysis.domain
        )
        return {
            "analysis": analysis,
            "goals": goals,
            "search_terms": terms,
        }
```

**Benefits of this pattern**:
- Type-safe data flow between agents
- Frontend Zod validation catches mismatches immediately
- Easy to swap implementations for testing
- No more "did I spell this key right?" debugging

---

## 5. Dependencies on Other Specs

| Spec | Dependency Type | Rationale |
|------|-----------------|-----------|
| Domain Model LLD | Locks entities | AgentSessionEntity, SessionState enum must remain stable |
| Agent Runtime LLD | Locks DSPy patterns | DSPy signatures, tools, LangGraph state machine patterns |
| C003 Agent Pipeline (archived) | Anti-pattern reference | Learn from what broke in previous LangGraph attempt |
| R014 UI Showcase | Working reference | DSPy+LangGraph patterns that work (but need optimization) |

---

## 6. Implementation Notes

### 6.1 File-by-File Changes

**Nodes (4 files, ~600 lines total)**:
- `agentx/agent/nodes/analyst.py` (188 lines) - Add asyncio.gather() for Pass 1 independent calls
- `agentx/agent/nodes/researcher.py` (119 lines) - Batch independent DSPy calls
- `agentx/agent/nodes/designer.py` (160 lines) - Batch independent DSPy calls
- `agentx/agent/nodes/contextualizer.py` (134 lines) - May benefit from async batching

**DSPy Tools (16 files, ~670 lines total)**:
- Analyst (5 modules): Add `aforward()` to each
- Researcher (5 modules): Add `aforward()` to each
- Designer (3 modules): Add `aforward()` to each
- Contextualizer (3 modules): Add `aforward()` to each

**Infrastructure**:
- `agentx/infrastructure/dspy_prewarm.py` (NEW) - Pre-warming service
- `agentx/core/config.py` (135 lines) - Add 4 new settings

### 6.2 Test-Backed Decisions

All implementation strategies are backed by test results (`tests/reports/SUMMARY.md`):

| Decision | Test Evidence |
|----------|---------------|
| Batch size = 4 | qwen3:8b shows 1.20x speedup @ 4 concurrent |
| Pre-warm 5 queries | Test shows 3-5 queries needed for warmup |
| Simple queries | Test shows simple queries work better |
| Use async | Test shows ASYNC wins at 1,4 concurrent for qwen3:8b |

---

**Next Artifact**: validate.md

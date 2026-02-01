# Spec: DSPy Performance Optimization

**Domain**: dspy-performance
**Generated**: 2026-02-01
**Status**: Draft

---

## 1. Purpose

Define the performance optimization layer for DSPy + LangGraph integration to prevent 60-second timeout failures. This spec covers model pre-warming, strategic async batching, and proper DSPy module patterns.

**Problem Statement**: LangGraph agent execution times out at 60+ seconds due to sequential DSPy calls, no model pre-warming, and blocking synchronous operations.

**Success Criteria**: Agent execution completes in ~20-25 seconds consistently (within 60s timeout margin).

---

## 2. Scope

### In Scope

- Model pre-warming service (3-5 warmup queries at startup)
- DSPy module `aforward()` async methods for all 16 tool modules
- Strategic async batching with `asyncio.gather()` in LangGraph nodes
- Configuration settings for batch size, pre-warming, and query simplicity
- Proper DSPy Signature classes (replacing string signatures)
- Pydantic data models for inter-agent communication
- Dependency injection patterns for testability

### Out of Scope

- Frontend changes (this is backend-only optimization)
- REST API changes (no new endpoints)
- Database schema changes
- New DSPy tools (only optimizing existing ones)
- LangGraph architecture redesign (only optimizing node execution)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-DSPY-001 | System must execute 3-5 warmup queries at startup before accepting user requests | Must | Test findings: pre-warming critical |
| FR-DSPY-002 | All 16 DSPy tool modules must implement `aforward()` method mirroring `forward()` | Must | DSPy async docs |
| FR-DSPY-003 | analyst.py Pass 1 must batch independent calls using `asyncio.gather()` | Must | scan.md section 4.1 |
| FR-DSPY-004 | researcher.py must batch independent DSPy calls | Must | scan.md section 3.1 |
| FR-DSPY-005 | designer.py must batch independent DSPy calls | Must | scan.md section 3.1 |
| FR-DSPY-006 | System must limit concurrent async calls to maximum 4 (configurable) | Must | Test: 4 concurrent optimal |
| FR-DSPY-007 | All string signatures must be replaced with proper Signature classes | Should | scan.md section 4.4 |
| FR-DSPY-008 | Pre-warming service must log duration for each warmup query | Should | Observability |
| FR-DSPY-009 | LangGraph nodes must use async node functions (`async def node(state):`) | Should | LangGraph docs |
| FR-DSPY-010 | Dependent DSPy calls must remain sequential even with async | Must | Dependency constraint |

### 3.2 Non-Functional Requirements

| ID | Requirement | Priority | Target Metric |
|----|-------------|----------|---------------|
| NFR-DSPY-001 | End-to-end agent execution time | Must | < 60s consistently |
| NFR-DSPY-002 | Per-query latency after pre-warming | Should | ~2s average |
| NFR-DSPY-003 | Pre-warming duration | Should | < 30s at startup |
| NFR-DSPY-004 | Code quality (Ruff, Pyrefly) | Must | All checks pass |
| NFR-DSPY-005 | Backwards compatibility | Must | Existing sync behavior preserved |
| NFR-DSPY-006 | Type safety | Should | Pydantic models for all inter-agent data |
| NFR-DSPY-007 | Testability | Should | Protocol-based DI for all services |

---

## 4. Data Model

### 4.1 Locked from LLD

```python
# From Domain Model LLD: docs/engineering/lld/domain_model.md
@dataclass
class AgentSessionEntity:
    """Agent session entity - locked from LLD."""
    session_id: UUID
    user_id: str  # SHA-256 hash
    state: SessionState
    current_reasoning_step: int
    total_tool_calls: int

    # Business methods
    def is_active(self) -> bool: ...
    def pause(self) -> None: ...
    def resume(self) -> None: ...
    def close(self) -> None: ...
    def increment_reasoning_step(self) -> None: ...
    def increment_tool_calls(self) -> None: ...

# SessionState enum
class SessionState(str, Enum):
    INITIALIZING = "INITIALIZING"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    CLOSED = "CLOSED"
```

### 4.2 Pydantic Data Models (New)

```python
# domain/models/dspy_models.py
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class QueryType(str, Enum):
    """Query classification types."""
    FACTUAL = "factual"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    PROCEDURAL = "procedural"

class AnalysisResult(BaseModel):
    """Output from analyst node - context analysis."""
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

class PrewarmStatus(BaseModel):
    """Status of DSPy model pre-warming."""
    is_prewarmed: bool = Field(description="Whether pre-warming completed")
    queries_executed: int = Field(description="Number of warmup queries run")
    total_duration_ms: float = Field(description="Total pre-warming duration")
    per_query_ms: list[float] = Field(default_factory=list, description="Duration per query")
```

### 4.3 Configuration Model

```python
# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Existing settings...

    # DSPy performance optimization settings
    dspy_prewarm_enabled: bool = True
    dspy_prewarm_queries: int = 5
    dspy_async_batch_size: int = 4  # Max concurrent async calls
    dspy_use_simple_queries: bool = True  # Avoid complex instructions

    class Config:
        env_file = ".env"
```

---

## 5. API Contract

### 5.1 REST Endpoints

| Method | Path | Request | Response | Status Codes | Purpose |
|--------|------|---------|----------|--------------|---------|
| GET | /api/v1/dspy/prewarm/status | - | `PrewarmStatus` | 200, 503 | Health check for pre-warming |

**Response Schema** (PrewarmStatus):
```json
{
  "is_prewarmed": true,
  "queries_executed": 5,
  "total_duration_ms": 27432.5,
  "per_query_ms": [6234.1, 5123.2, 4891.3, 4701.8, 6482.1]
}
```

### 5.2 WebSocket Channels

(None - backend optimization only)

---

## 6. Business Rules

| Rule | Description | Enforcement | Source |
|------|-------------|-------------|--------|
| BR-DSPY-001 | Pre-warming must complete before accepting user requests | Code block in startup | Test findings |
| BR-DSPY-002 | Maximum 4 concurrent async calls (configurable) | Configuration enforcement | Test: optimal at 4 |
| BR-DSPY-003 | Independent calls batched, dependent calls sequential | Code pattern in nodes | Dependency analysis |
| BR-DSPY-004 | Simple queries preferred over complex instructions | Configuration flag | Test findings |
| BR-DSPY-005 | All DSPy modules must have both `forward()` and `aforward()` | Code pattern | DSPy async docs |
| BR-DSPY-006 | Signature classes replace string signatures | Code review | Pydantic warnings |

---

## 7. Acceptance Criteria

- [ ] Pre-warming service executes 5 warmup queries at startup
- [ ] All 16 DSPy tool modules have `aforward()` methods implemented
- [ ] analyst.py Pass 1 uses `asyncio.gather()` for 2 independent calls (context_analyzer, insight_extractor)
- [ ] researcher.py batches independent DSPy calls with `asyncio.gather()`
- [ ] designer.py batches independent DSPy calls with `asyncio.gather()`
- [ ] Configuration settings added to `agentx/core/config.py`
- [ ] All string signatures replaced with proper Signature classes
- [ ] End-to-end execution completes in <60s consistently
- [ ] Ruff checks pass for all modified files
- [ ] Pyrefly checks pass for all modified files
- [ ] Pre-warming status endpoint returns correct data
- [ ] Existing sync behavior is preserved (backwards compatible)

---

## 8. Test Scenarios

### 8.1 Pre-warming Tests

| Scenario | Steps | Expected Result |
|----------|-------|-----------------|
| Cold start | 1. Start backend<br>2. Check pre-warm status | Pre-warming runs 5 queries, completes in <30s |
| Warm start | 1. Restart backend<br>2. Check pre-warm status | Pre-warming runs again (no cache) |
| Pre-warm disabled | 1. Set DSPY_PREWARM_ENABLED=false<br>2. Start backend | Pre-warming skipped, requests accepted immediately |

### 8.2 Async Batching Tests

| Scenario | Steps | Expected Result |
|----------|-------|-----------------|
| Independent calls | 1. Call analyst.py Pass 1<br>2. Measure duration | ~12-16s (vs 24-32s sequential) |
| Dependent calls | 1. Call goal_detector after insights<br>2. Verify order | Sequential execution, correct data flow |
| Batch size limit | 1. Set DSPY_ASYNC_BATCH_SIZE=4<br>2. Execute 6 calls | 4 concurrent, then remaining 2 |

### 8.3 Integration Tests

| Scenario | Steps | Expected Result |
|----------|-------|-----------------|
| End-to-end | 1. Send user query<br>2. Wait for response | <60s total execution time |
| Backwards compatibility | 1. Call old sync APIs | Existing behavior preserved |

---

## 9. References

- **LangGraph Graph API**: `tests/langgraph_graph_api.md` (723 lines) - StateGraph, nodes, edges, reducers
- **LangGraph Workflows & Agents**: `tests/langgraph_workflows_agents.md` (1113 lines) - Parallel execution patterns
- **DSPy Async Tutorial**: `/home/riju279/Downloads/dspy-main/dspy-main/docs/docs/tutorials/async/index.md`
- **Test Results**: `tests/reports/SUMMARY.md` - Performance benchmarks
- **Domain Model LLD**: `docs/engineering/lld/domain_model.md` - AgentSessionEntity definition

---

**Next**: Design artifact will define technical implementation approach.

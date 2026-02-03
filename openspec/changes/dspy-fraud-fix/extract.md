# Extract Artifact: dspy-fraud-fix

**Generated**: 2026-02-03
**Change**: dspy-fraud-fix
**Schema**: spec-factory v1.0.0

---

## 1. Pattern Catalog

### 1.1 Architectural Patterns

| Pattern | Source | Description | Apply? |
|---------|--------|-------------|--------|
| Clean Architecture | LLD domain_model.md | Layered separation with domain independence | ✅ PRESERVE |
| Repository Pattern | LLD domain_model.md | ABC base + implementations in infrastructure | ✅ PRESERVE |
| DTO Pattern | LLD domain_model.md | Pydantic models for API layer | ✅ PRESERVE |
| DSPy Module Pattern | DSPy docs | `dspy.Module` base with `forward()` returning `dspy.Prediction` | ✅ FIX NEEDED |
| DSPy Retrieval Pattern | DSPy docs | `dspy.Retrieve` or custom retriever class | ❌ FAKE RAG - FIX |
| DSPy ReAct Pattern | DSPy docs | `dspy.ReAct()` with tools for multi-step reasoning | ✅ ENHANCE |
| LangGraph Send API | dynamic_agent_graph.py | Dynamic worker creation via `Send` | ✅ PRESERVE |
| Mem0 Integration | mem0_adapter.py | Mem0 wraps QdrantVectorStore with ColBERTv2 | ✅ ENHANCE |

### 1.2 Code Structure Patterns

| Pattern | Example | Apply? |
|---------|---------|--------|
| @dataclass entities | `class AgentSessionEntity:` | ✅ PRESERVE |
| ABC repositories | `class AgentSessionRepository(ABC):` | ✅ PRESERVE |
| Static mappers | `@staticmethod def to_dto()` | ✅ PRESERVE |
| Use case classes | `class CreateSessionUseCase:` | ✅ PRESERVE |
| DSPy Class Signatures | `class MySignature(dspy.Signature):` | ✅ REQUIRED |
| DSPy Module forward | `def forward(self, ...) -> dspy.Prediction:` | ✅ REQUIRED |
| Mem0-powered retrieval | Mem0MemoryAdapter.search_memories() | ❌ REPLACE FAKE |
| Query Planner Enhancement | QueryPlannerModule with memory guidance | ✅ ENHANCE |

### 1.3 Naming Patterns (to Avoid from R014)

| R014 Name | Why Avoid | Alternative |
|-----------|-----------|-------------|
| `RAGDSPyAgent` | Misleading - uses `dspy.Predict` not real retrieval | `RAGContextGenerator` |
| `MemoryAgent` | Fake memory - uses `dspy.Predict` not real Mem0 access | `Mem0RetrievalAgent` |
| Widget-related names | Dead code exists | Remove unused code |
| Inline signatures | Weak LLM incompatible (gemma3:4b) | Class-based signatures |
| Dict returns | Wrong type - should return `dspy.Prediction` | Wrap in `dspy.Prediction()` |

---

## 2. Specification Drafts

### 2.1 Draft: Work-Experience Memory Schema Spec

**Purpose**: Define memory schema for work-experience based storage (NOT fact storage)

**Fraud Issues Addressed**: Foundation for memory system

**Scope**:
- In scope: MemoryRecord entity with work-experience fields (data_input, instruction_input, reasoning_done, output_produced)
- In scope: Quality scoring, TTL, supersede, decay mechanisms
- Out of scope: Fact/knowledge storage (memory stores WORK experience, not arbitrary content)

**Locked from LLD**:
```python
# From domain_model.md - LOCKED entities to extend
@dataclass
class AgentSessionEntity:
    session_id: UUID
    user_id: str
    state: SessionState
    created_at: datetime
    modified_at: datetime
    last_activity_at: datetime
```

**Requirements**:
1. MemoryRecord entity stores work-experience: data received, instructions followed, reasoning performed, output produced
2. Quality score (0.0-1.0) tracks how good the work was
3. TTL (time-to-live) with extension on good retrieval, shortening on bad retrieval
4. Supersede mechanism: better memory replaces older one
5. Decay mechanism: quality score degrades over time
6. Access count tracking for reinforcement learning

**Acceptance Criteria** (HARD VALIDATION):
- [ ] MemoryRecord entity exists with fields: data_input, instruction_input, reasoning_done, output_produced, quality_score, access_count, ttl_days, superseded_by
- [ ] WorkExperienceType enum exists with values: DATA_RECEIVED, INSTRUCTION_FOLLOWED, REASONING_DONE, OUTPUT_PRODUCED
- [ ] Can create MemoryRecord instance: `record = MemoryRecord(user_id='test', memory_type=WorkExperienceType.OUTPUT_PRODUCED, ...)`
- [ ] MemoryRecord validation prevents storing arbitrary facts (only work-experience)
- [ ] Quality score is required float between 0.0 and 1.0
- [ ] TTL days is positive integer
- [ ] File passes: `ruff check` and `pyrefly check`

**Files to Create**:
- `agentx/domain/entities/memory_record.py` (NEW)

---

### 2.2 Draft: Session Performance Tracking Spec

**Purpose**: Enable LangGraph routing decisions based on session performance history

**Fraud Issues Addressed**: Foundation for adaptive routing

**Scope**:
- In scope: SessionPerformance entity tracking route_taken, overall_outcome
- In scope: RoutingDecisionService for suggesting routing strategies
- In scope: RouteOutcome enum (GOOD, AVERAGE, BAD)
- Out of scope: Actual routing logic (handled by LangGraph)

**Locked from LLD**:
```python
# From domain_model.md - LOCKED AgentStatus enum
class AgentStatus(str, Enum):
    IDLE = "idle"
    THINKING = "thinking"
    USING_TOOL = "using_tool"
    COMPLETED = "completed"
    FAILED = "failed"
```

**Requirements**:
1. SessionPerformance tracks: session_id, user_id, query, route_taken (list of agent steps), overall_outcome
2. AgentStep captures: agent_name, duration_ms, success, quality_score
3. RouteOutcome: GOOD, AVERAGE, BAD
4. RoutingDecisionService suggests: "similar" (use same route), "different" (try new), "augment" (add agents), "shorten" (skip agents)
5. Service queries session performance history to make routing suggestions

**Acceptance Criteria** (HARD VALIDATION):
- [ ] SessionPerformance entity exists with required fields
- [ ] AgentStep dataclass exists with agent_name, duration_ms, success, quality_score
- [ ] RouteOutcome enum exists: GOOD, AVERAGE, BAD
- [ ] RoutingDecisionService.suggest_routing() returns dict with "strategy" key
- [ ] Service can record and retrieve session performance
- [ ] File passes: `ruff check` and `pyrefly check`

**Files to Create**:
- `agentx/domain/entities/session_performance.py` (NEW)
- `agentx/application/services/routing_decision_service.py` (NEW)
- `agentx/agent/nodes/routing_performance.py` (NEW)

---

### 2.3 Draft: Memory-Guided Search Planning Spec

**Purpose**: Memory guides HOW to search (ALWAYS search happens, memory determines depth/terms/sources/format)

**Fraud Issues Addressed**: Enhances existing QueryPlannerModule without breaking it

**Scope**:
- In scope: ENHANCE existing QueryPlannerModule with memory guidance
- In scope: SearchGuidanceModule for retrieving user preferences from memory
- In scope: Memory provides: search_depth, prioritized_terms, source_preferences, answer_format
- In scope: Integration with SearchTermPatternMemory (NEW - see spec 2.12)
- Out of scope: Replacing ExecutionPlan generation (MUST PRESERVE 0 to N tasks pattern)
- Out of scope: Cache lookup logic (MUST PRESERVE)

**CRITICAL PRESERVATION**:
```python
# EXISTING pattern to PRESERVE from query_planner.py
class QueryPlannerModule(dspy.Module):
    def forward(self, query: str, **kwargs) -> dspy.Prediction:
        # Generates ExecutionPlan with 0 to N research tasks
        # 0 tasks = direct answer (cache hit or simple query)
        # N tasks = research needed
```

**Requirements**:
1. Create SearchGuidanceModule that retrieves user preferences from memory
2. ENHANCE QueryPlannerModule to use memory guidance (NOT replace)
3. Memory stores: search patterns that worked, user preferences (sources, depth, format)
4. Memory does NOT store facts/knowledge
5. ExecutionPlan format preserved: 0 tasks = direct answer, N tasks = research
6. Cache lookup checked BEFORE executing tasks (preserved)

**Acceptance Criteria** (HARD VALIDATION):
- [ ] SearchGuidanceModule exists and retrieves from memory
- [ ] SearchGuidance returns: search_depth, prioritized_terms, source_preferences, answer_format
- [ ] QueryPlannerModule still generates ExecutionPlan with 0 to N tasks
- [ ] QueryPlannerModule preserves cache lookup logic
- [ ] Direct answer path still works (0 tasks)
- [ ] Memory guidance is optional enhancement, not replacement
- [ ] File passes: `ruff check` and `pyrefly check`

**Files to Modify**:
- `agentx/agent/nodes/query_planner.py` (ENHANCE, not replace)
- `agentx/agent/dspy_signatures/decision_signatures.py` (NEW)

---

### 2.4 Draft: Adaptive Retrieval Spec

**Purpose**: Retrieve until quality score drops below threshold (not fixed k=10)

**Fraud Issues Addressed**: Foundation for quality-based retrieval

**Scope**:
- In scope: Quality-based retrieval filtering
- In scope: k=20 max candidates, quality_threshold=0.6, min_results=3
- Out of scope: Changing embedding model (use existing ColBERTv2)

**Requirements**:
1. Retrieve k candidates from Mem0 (default k=20)
2. Filter: keep while quality >= threshold OR until min_results reached
3. Quality threshold configurable (default 0.6)
4. Minimum results guaranteed (default 3)
5. Return filtered list with quality scores

**Acceptance Criteria** (HARD VALIDATION):
- [ ] Mem0DSPyRetriever supports adaptive retrieval
- [ ] Retrieval stops when quality score drops below threshold
- [ ] Returns at least min_results even if below threshold
- [ ] Configurable quality_threshold parameter
- [ ] Returns filtered list with scores
- [ ] File passes: `ruff check` and `pyrefly check`

**Files to Modify**:
- `agentx/infrastructure/retrieval/mem0_dspy_retriever.py` (NEW)
- `agentx/infrastructure/memory/mem0_adapter.py` (update)

---

### 2.5 Draft: Context Rotting Prevention Spec

**Purpose**: TTL + supersede + decay + reinforcement mechanisms

**Fraud Issues Addressed**: Foundation for memory hygiene

**Scope**:
- In scope: ContextRotManager for TTL, decay, supersede
- In scope: ReinforcementTracker for logging retrieval outcomes
- In scope: TTL extension on good retrieval, shortening on bad retrieval
- Out of scope: Memory storage logic (separate concern)

**Requirements**:
1. TTL: Memories expire after ttl_days
2. Supersede: Better memory replaces older one (superseded_by field)
3. Decay: Quality score degrades over time
4. Reinforcement: Good retrievals extend TTL, bad retrievals shorten TTL
5. Configurable base_ttl_days, ttl_extension_days, ttl_shorten_days

**Acceptance Criteria** (HARD VALIDATION):
- [ ] ContextRotManager exists with check_ttl(), apply_decay(), handle_supersede()
- [ ] ReinforcementTracker exists with log_retrieval_outcome()
- [ ] TTL is checked and enforced
- [ ] Quality decay is applied over time
- [ ] Supersede mechanism works (superseded_by field)
- [ ] Good retrievals extend TTL, bad retrievals shorten TTL
- [ ] File passes: `ruff check` and `pyrefly check`

**Files to Create**:
- `agentx/infrastructure/memory/context_rot_manager.py` (NEW)
- `agentx/infrastructure/memory/reinforcement_tracker.py` (NEW)

---

### 2.6 Draft: Real RAG Implementation Spec

**Purpose**: Replace fake RAG (dspy.Predict) with real Mem0-powered retrieval + RAG conflict resolution

**Fraud Issues Addressed**: Fraud #1 - Fake RAG in rag_agent.py

**Scope**:
- In scope: Replace dspy.Predict with real Mem0 retrieval
- In scope: Mem0DSPyRetriever wrapping Mem0MemoryAdapter
- In scope: All components use SAME ColBERTv2 embeddings
- In scope: Source attribution and confidence tracking (for conflict resolution)
- In scope: Integration with RAGConflictResolutionService (NEW - see spec 2.13)
- Out of scope: Changing embedding model (ColBERTv2 is standard)

**Current Anti-Pattern** (from fraud analysis):
```python
# WRONG - Fake RAG using dspy.Predict
class RAGDSPyAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.retrieve = dspy.Predict(...)  # ❌ FAKE
```

**Required Pattern**:
```python
# CORRECT - Real RAG using Mem0 wrapper
from agentx.infrastructure.retrieval.mem0_dspy_retriever import Mem0DSPyRetriever

class RAGContextGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.retrieve = Mem0DSPyRetriever(k=10)  # ✅ REAL
```

**Requirements**:
1. Create Mem0DSPyRetriever that wraps Mem0MemoryAdapter
2. Use ColBERTv2 embeddings (already configured in QdrantVectorStore)
3. Retrieve via Mem0.search_memories() (uses ColBERTv2)
4. Format results for DSPy (objects with long_text attribute)
5. Replace dspy.Predict in RAGDSPyAgent with real retrieval

**Acceptance Criteria** (HARD VALIDATION):
- [ ] Mem0DSPyRetriever class exists in infrastructure/retrieval/
- [ ] RAGDSPyAgent uses Mem0DSPyRetriever (not dspy.Predict)
- [ ] Mem0DSPyRetriever returns list of objects with long_text attribute
- [ ] Retrieval uses Mem0MemoryAdapter.search_memories()
- [ ] All components use ColBERTv2 (colbert-ir/colbertv2.0)
- [ ] No dspy.Predict used for retrieval (only for LLM processing)
- [ ] File passes: `ruff check` and `pyrefly check`

**Files to Create/Modify**:
- `agentx/infrastructure/retrieval/mem0_dspy_retriever.py` (NEW)
- `agentx/agent/dspy_agents/rag_agent.py` (modify)

---

### 2.7 Draft: Multi-Source Synthesis Spec

**Purpose**: Synthesize multiple research sources into unified answer with conflict resolution fallback

**Fraud Issues Addressed**: Missing synthesis service for research results + RAG contradiction handling

**Scope**:
- In scope: SynthesisService for combining research sources
- In scope: MultiSourceSynthesisSignature
- In scope: Consensus points, conflicts detection
- In scope: Fallback to DSPy LLM-mediated resolution when tiered conflict resolution fails (see spec 2.13)
- Out of scope: Research execution (handled by existing nodes)

**Requirements**:
1. SynthesisService combines multiple assessed sources
2. Returns: unified_answer, consensus_points, conflicts
3. Uses DSPy ChainOfThought for synthesis
4. Handles JSON input of assessed sources

**Acceptance Criteria** (HARD VALIDATION):
- [ ] SynthesisService exists in application/services/
- [ ] MultiSourceSynthesisSignature exists in dspy_signatures/
- [ ] synthesize() method returns dict with unified_answer, consensus_points, conflicts
- [ ] Uses dspy.ChainOfThought or Predict
- [ ] Handles JSON input of assessed sources
- [ ] File passes: `ruff check` and `pyrefly check`

**Files to Create**:
- `agentx/application/services/synthesis_service.py` (NEW)
- `agentx/agent/dspy_signatures/synthesis_signatures.py` (NEW)

---

### 2.8 Draft: DSPy Signature Replacements Spec

**Purpose**: Replace all inline signatures with class-based signatures

**Fraud Issues Addressed**: Fraud #6-17 (12 inline signature violations)

**Scope**:
- In scope: Create proper signature classes in dspy_signatures/
- In scope: Update all 24 tool modules to use class-based signatures
- In scope: Signatures compatible with gemma3:4b (weak LLM)
- Out of scope: Changing module logic (only signature usage)

**Current Anti-Pattern** (from fraud analysis):
```python
# WRONG - Inline signature (weak LLM incompatible)
def forward(self, query: str) -> dspy.Prediction:
    predict = dspy.Predict(
        "query: str -> query_type: str, domain: str, urgency: str"
    )
    result = predict(query=query)
    return dspy.Prediction(query_type=result.query_type, ...)
```

**Required Pattern**:
```python
# CORRECT - Class-based signature (weak LLM compatible)
class QueryAnalysisSignature(dspy.Signature):
    """Analyze query type, domain, and urgency."""
    query: str = dspy.InputField(desc="User's question or request")
    query_type: str = dspy.OutputField(desc="Type: question, task, analysis, or comparison")
    domain: str = dspy.OutputField(desc="Domain: health, finance, tech, travel, general")
    urgency: str = dspy.OutputField(desc="Urgency: routine, urgent, critical")

class ContextAnalyzerModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.analyze = dspy.Predict(QueryAnalysisSignature)  # ✅ Class-based
```

**Requirements**:
1. Create signature classes in dspy_signatures/ subdirectory:
   - analyst.py (QueryTypeSignature, QueryDomainSignature, QueryUrgencySignature, GoalDetectionSignature)
   - researcher.py (CitationSignature, DataStructureSignature, FindingsFormatSignature)
   - presenter.py (QualityCheckSignature, PresentationSignature)
   - designer.py (ColorSchemeSignature, HierarchySignature, POVSignature)
   - contextualizer.py (RelevanceScoreSignature, ContextInjectionSignature, FilterDecisionSignature)
2. Update all tool modules to use class-based signatures
3. Each signature has explicit field descriptions for gemma3:4b compatibility

**Acceptance Criteria** (HARD VALIDATION):
- [ ] analyst.py signature file exists with 4 signatures
- [ ] researcher.py signature file exists with 3 signatures
- [ ] presenter.py signature file exists with 2 signatures
- [ ] designer.py signature file exists with 3 signatures
- [ ] contextualizer.py signature file exists with 3 signatures
- [ ] All tool modules updated to use class-based signatures
- [ ] No dspy.Predict(string) calls with inline signatures
- [ ] All signatures have explicit field descriptions
- [ ] All files pass: `ruff check` and `pyrefly check`

**Files to Create/Modify**:
- `agentx/agent/dspy_signatures/analyst.py` (NEW)
- `agentx/agent/dspy_signatures/researcher.py` (NEW)
- `agentx/agent/dspy_signatures/presenter.py` (NEW)
- `agentx/agent/dspy_signatures/designer.py` (NEW)
- `agentx/agent/dspy_signatures/contextualizer.py` (NEW)
- All 24 tool modules in agentx/agent/tools/ (modify)

---

### 2.9 Draft: Return Type Fixes Spec

**Purpose**: Fix all modules returning dict instead of dspy.Prediction

**Fraud Issues Addressed**: Fraud #18-41 (24 modules with wrong return types)

**Scope**:
- In scope: Wrap all dict returns in dspy.Prediction
- In scope: All tool modules return dspy.Prediction
- Out of scope: Changing module logic (only return type)

**Current Anti-Pattern** (from fraud analysis):
```python
# WRONG - Returns dict
def forward(self, query: str) -> dict:
    result = self.analyzer(query=query)
    return {"query_type": result.query_type, "domain": result.domain}
```

**Required Pattern**:
```python
# CORRECT - Returns dspy.Prediction
def forward(self, query: str) -> dspy.Prediction:
    result = self.analyzer(query=query)
    return dspy.Prediction(
        query_type=result.query_type,
        domain=result.domain
    )
```

**Requirements**:
1. All 24 tool modules return dspy.Prediction
2. Dict values wrapped in dspy.Prediction constructor
3. Type hints updated to return dspy.Prediction

**Affected Modules** (24 total):
- analyst/: context_analyzer.py, goal_detector.py, search_terms.py, insight_extractor.py, data_quality_checker.py
- researcher/: citation_builder.py, data_structurer.py, findings_beautifier.py
- presenter/: quality_check.py, presentation.py
- contextualizer/: reranker.py, contextualizer.py, filter.py
- designer/: color_scheme.py, hierarchy.py, pov_generator.py
- (all remaining tool modules)

**Acceptance Criteria** (HARD VALIDATION):
- [ ] All 24 tool modules return dspy.Prediction
- [ ] No modules return dict
- [ ] Type hints updated to -> dspy.Prediction
- [ ] All files pass: `ruff check` and `pyrefly check`
- [ ] Verification script passes:
```python
# Verify no dict returns
import ast
import os
for root, dirs, files in os.walk('agentx/agent/tools'):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            with open(path) as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Return):
                    # Check for dict literal in return
                    if isinstance(node.value, ast.Dict):
                        print(f'❌ {path}: Returns dict literal')
```

**Files to Modify**:
- All 24 tool modules in agentx/agent/tools/

---

### 2.10 Draft: DSPy Caching Spec

**Purpose**: Enable DSPy caching for performance

**Fraud Issues Addressed**: Fraud #53 - cache=False in dspy.py

**Scope**:
- In scope: Enable DSPy LM caching
- Out of scope: Cache invalidation (handled by DSPy)

**Current Anti-Pattern** (from fraud analysis):
```python
# WRONG - Cache disabled
lm = dspy.LM(
    model=f"ollama_chat/{model}",
    api_base=settings.ollama_base_url,
    cache=False,  # ❌ Disabled
)
```

**Required Pattern**:
```python
# CORRECT - Cache enabled
lm = dspy.LM(
    model=f"ollama_chat/{model}",
    api_base=settings.ollama_base_url,
    cache=True,  # ✅ Enabled
)
```

**Requirements**:
1. Change cache=False to cache=True in dspy.py
2. No other changes needed

**Acceptance Criteria** (HARD VALIDATION):
- [ ] dspy.py has cache=True in LM configuration
- [ ] File passes: `ruff check` and `pyrefly check`
- [ ] Verification:
```bash
grep -n "cache=" agentx/core/dependency_facades/dspy.py | grep -i "true"
```

**Files to Modify**:
- `agentx/core/dependency_facades/dspy.py` (1 line change)

---

### 2.11 Draft: Search Term Pattern Memory Spec

**Purpose**: Learn from past successful search terms and predict terms for new queries

**Problem Statement**: SearchTermExtractorModule (R014) extracts terms via multi-iteration DSPy, but doesn't learn from past successes. For topic A, terms X,Y,Z worked; for topic B, what terms will work?

**Scope**:
- In scope: SearchTermPatternMemory entity tracking query → search_terms → result_quality
- In scope: Pattern extraction: "For [topic_type], terms [X,Y,Z] work well"
- In scope: Term prediction for new queries based on similarity
- In scope: Integration with SearchTermExtractorModule (from R014 - already ported)
- Out of scope: SearchTermExtractorModule itself (PRESERVE existing)

**Requirements**:
1. SearchTermPatternMemory tracks: original_query, search_terms_used, result_quality_score, timestamp, topic_type
2. Pattern learning: Group successful searches by topic_type, extract common term patterns
3. Term prediction: For new query, retrieve similar topic patterns, suggest terms
4. Quality feedback: Record which terms produced good results (>0.7 quality)
5. Term diversity: Encourage varied term selection (avoid term repetition)

**Acceptance Criteria** (HARD VALIDATION):
- [ ] SearchTermPatternMemory entity exists with required fields
- [ ] Pattern extraction logic: "For health queries about [fruit], terms [X, Y, Z] work"
- [ ] Term prediction: "For new topic, try these terms based on similar past topics"
- [ ] Integration with SearchTermExtractorModule
- [ ] Quality feedback loop: Successful terms reinforce pattern
- [ ] File passes: `ruff check` and `pyrefly check`

**Files to Create**:
- `agentx/domain/entities/search_term_pattern.py` (NEW)
- `agentx/application/services/search_term_pattern_service.py` (NEW)

**Related Specs**:
- `specs/memory_guided_search/spec.md` - Uses search term patterns for guidance
- `specs/searxng_hybrid_search/spec.md` - Integrates with SearXNG search

---

### 2.12 Draft: RAG Conflict Resolution Spec

**Purpose**: Resolve contradictions between retrieved memories using tiered strategy + LLM fallback

**Problem Statement**: RAG fails when contradicting facts load into context. Need protection against misinformation.

**Scope**:
- In scope: Source attribution (each memory tracks source)
- In scope: Confidence-based filtering (highest confidence wins)
- In scope: Source authority weighting (academic > general > social)
- In scope: Temporal priority (newest memory wins for same topic)
- In scope: LLM-mediated resolution (DSPy synthesis) as fallback
- Out of scope: Memory storage logic (separate concern)

**Tiered Conflict Resolution Strategy**:
```
Tier 1: Temporal Priority
  - For same topic: Newest memory wins
  - Supersede mechanism: Better memory replaces older

Tier 2: Confidence Score
  - If timestamps equal or different topics: Highest confidence_score wins
  - Filter: quality >= 0.7 (high confidence threshold)

Tier 3: Source Authority
  - If confidence equal: Source type priority
  - academic > report > general > social > unknown

Tier 4: LLM-Mediated Resolution (Fallback)
  - If confusion remains after tiers 1-3
  - Use DSPy synthesis to resolve
  - Explicit contradiction handling: "Sources disagree: A says X, B says Y"
```

**Requirements**:
1. Each memory tracks: source_type, confidence_score, created_at
2. Tier 1: Newest memory wins for same topic (supersede mechanism)
3. Tier 2: Filter by confidence >= threshold, pick highest
4. Tier 3: Source authority enum (ACADEMIC, REPORT, GENERAL, SOCIAL, UNKNOWN)
5. Tier 4: DSPy synthesis for remaining conflicts

**Acceptance Criteria** (HARD VALIDATION):
- [ ] MemoryRecord has source_type, confidence_score fields
- [ ] Conflict resolution follows 4-tier strategy
- [ ] Temporal priority works (newest wins same topic)
- [ ] Confidence filtering works (highest >= threshold wins)
- [ ] Source authority weighting works
- [ ] DSPy synthesis fallback for remaining conflicts
- [ ] File passes: `ruff check` and `pyrefly check`

**Files to Create/Modify**:
- `agentx/domain/entities/memory_record.py` (extend: add source_type)
- `agentx/application/services/rag_conflict_resolution_service.py` (NEW)

**Related Specs**:
- `specs/real_rag/spec.md` - Enhanced with conflict resolution
- `specs/multi_source_synthesis/spec.md` - Uses LLM fallback

---

### 2.13 Draft: SearXNG Hybrid Search Spec

**Purpose**: Hybrid approach: RAG for stored facts + SearXNG for current/predictive info

**Problem Statement**: RAG only covers stored knowledge. Need fresh web search for current events, predictions, niche topics.

**Scope**:
- In scope: Hybrid RAG + SearXNG approach
- In scope: SearchTermExtractorModule (from R014 - already ported)
- In scope: Integration with SearchTermPatternMemory for term prediction
- In scope: Decision logic: when to use RAG vs SearXNG vs both
- Out of scope: SearchTermExtractorModule itself (PRESERVE existing)

**Hybrid Strategy**:
```
Query Analysis:
├─ Niche/Current Topic? → SearXNG (fresh web data)
├─ Well-Established Topic? → RAG (stored knowledge)
├─ Contradicting Info? → SearXNG (verify current)
└─ Complex Query? → Both (RAG + SearXNG synthesis)

Search Term Prediction:
├─ Retrieve past successful patterns from SearchTermPatternMemory
├─ "For [topic], terms [X,Y,Z] worked"
└─ Predict terms for new query

SearXNG Execution:
├─ SearchTermExtractorModule (R014: multi-iteration term extraction)
├─ SearXNGClient.search(terms)
└─ Result: fresh web sources
```

**Requirements**:
1. Decision logic: RAG vs SearXNG vs both
2. SearchTermPatternMemory integration for term prediction
3. SearchTermExtractorModule (PRESERVE from R014)
4. SearXNG client integration (PRESERVE existing)
5. Hybrid synthesis: combine RAG + SearXNG results

**Acceptance Criteria** (HARD VALIDATION):
- [ ] Decision logic exists: when to use RAG vs SearXNG
- [ ] SearchTermPatternMemory predicts terms based on past patterns
- [ ] SearchTermExtractorModule preserved (R014 mechanism)
- [ ] Hybrid synthesis combines RAG + SearXNG results
- [ ] File passes: `ruff check` and `pyrefly check`

**Files to Create/Modify**:
- `agentx/agent/tools/analyst/search_terms.py` (PRESERVE - already ported from R014)
- `agentx/application/services/hybrid_search_service.py` (NEW)
- `agentx/agent/tools/researcher/search_executor.py` (PRESERVE SearXNG integration)

**Related Specs**:
- `specs/search_term_pattern_memory/spec.md` - Provides term prediction
- `specs/memory_guided_search/spec.md` - Uses term patterns for guidance

---

### 2.14 Draft: Quality Filtering Spec

**Purpose**: Enable actual quality-based filtering in reranker

**Fraud Issues Addressed**: Fraud #5 - reranker computes scores but doesn't filter

**Scope**:
- In scope: Add filtering logic to reranker
- In scope: Threshold parameter for filtering
- Out of scope: Changing scoring logic

**Current Anti-Pattern** (from fraud analysis):
```python
# WRONG - No filtering
def forward(self, context: List[str], query: str) -> dict:
    results = []
    for ctx in context:
        result = self.scorer(context=ctx, query=query)
        results.append({'context': ctx, 'quality_score': result.quality_score})
    return {'results': results}  # ❌ Returns all, no filtering
```

**Required Pattern**:
```python
# CORRECT - Actually filters
def forward(self, context: List[str], query: str, threshold: float = 0.6) -> dspy.Prediction:
    results = []
    for ctx in context:
        result = self.scorer(context=ctx, query=query)
        if result.quality_score >= threshold:  # ✅ Filter by threshold
            results.append({'context': ctx, 'quality_score': result.quality_score})

    return dspy.Prediction(
        filtered_results=results,
        original_count=len(context),
        filtered_count=len(results)
    )
```

**Requirements**:
1. Add quality threshold parameter (default 0.6)
2. Filter results by quality_score >= threshold
3. Return filtered list with counts
4. Return type is dspy.Prediction

**Acceptance Criteria** (HARD VALIDATION):
- [ ] reranker.py filters results by threshold
- [ ] Default threshold is 0.6
- [ ] Returns dspy.Prediction with filtered_results, original_count, filtered_count
- [ ] File passes: `ruff check` and `pyrefly check`

**Files to Modify**:
- `agentx/agent/tools/contextualizer/reranker.py`

---

## 3. API Contracts

### 3.1 REST Endpoints

| Method | Path | Request | Response |
|--------|------|---------|----------|
| (No new REST endpoints for this change - DSPy/internal only) |

### 3.2 WebSocket Channels

| Channel | Message Type | Schema |
|---------|--------------|--------|
| (No new WebSocket channels for this change) |

### 3.3 Port Assignments

| Service | Port | Purpose |
|---------|------|---------|
| (No new services - uses existing infrastructure) |

---

## 4. Data Model Mappings

### 4.1 Pydantic → Zod Mappings

| Pydantic Model | Zod Type | Notes |
|----------------|----------|-------|
| (No frontend changes for DSPy fixes) |

### 4.2 Shared Types

(No frontend/backend shared types for DSPy fixes - this is backend-only change)

---

## 5. Dependencies on Other Specs

| Spec | Dependency Type | Rationale |
|------|-----------------|-----------|
| None | - | Self-contained DSPy fixes |

---

## Summary

**Total Spec Drafts**: 14
**Foundation Specs** (Phase 0): 5
- Work-Experience Memory Schema
- Session Performance Tracking
- Memory-Guided Search Planning (enhanced with SearchTermPatternMemory)
- Adaptive Retrieval
- Context Rotting Prevention

**Critical Content Specs** (Phase 1): 5
- Real RAG Implementation (enhanced with conflict resolution)
- Multi-Source Synthesis (enhanced with LLM fallback)
- **NEW: Search Term Pattern Memory** (learns from past successful searches)
- **NEW: RAG Conflict Resolution** (tiered strategy + LLM fallback)
- **NEW: SearXNG Hybrid Search** (RAG + SearXNG decision logic)

**Anti-Pattern Specs** (Phase 2): 4
- DSPy Signature Replacements
- Return Type Fixes
- DSPy Caching
- Quality Filtering

**Implementation Batches**: 17 batches across 4 phases (from plan, includes 3 new batches for Phase 1b)

---

**Next Artifact**: validate.md

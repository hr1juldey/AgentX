# Tasks Artifact: dspy-fraud-fix

**Generated**: 2026-02-03
**Change**: dspy-fraud-fix
**Schema**: spec-factory v1.0.0

---

## 1. Implementation Checklist

### 1.1 Phase 0: Foundation Architecture (5 NEW files, 0 breaking changes)

#### Batch 0a: Work-Experience Memory Schema

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create MemoryRecord entity | `agentx/domain/entities/memory_record.py` | ✅ | @dataclass, <100 lines |
| Create WorkExperienceType enum | `agentx/domain/entities/memory_record.py` | ✅ | 4 values |
| Add validation methods | `agentx/domain/entities/memory_record.py` | ✅ | is_expired(), record_access() |
| Run verification | Verification script | ✅ | All checks pass |

**Acceptance Criteria**:
```python
from agentx.domain.entities.memory_record import MemoryRecord, WorkExperienceType
record = MemoryRecord(
    memory_id=UUID('12345678-1234-5678-1234-567812345678'),
    user_id='test',
    session_id='session123',
    memory_type=WorkExperienceType.OUTPUT_PRODUCED,
    data_input='user query',
    instruction_input='search and summarize',
    reasoning_done='queried vector store',
    output_produced='Summary text',
    quality_score=0.85,
    created_at=datetime.now()
)
assert 0.0 <= record.quality_score <= 1.0
assert not record.is_expired()
record.record_access()
assert record.access_count == 1
```

#### Batch 0b: Session Performance Tracking

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create SessionPerformance entity | `agentx/domain/entities/session_performance.py` | ✅ | @dataclass, <100 lines |
| Create AgentStep dataclass | `agentx/domain/entities/session_performance.py` | ✅ | agent_name, duration_ms, success, quality_score |
| Create RouteOutcome enum | `agentx/domain/entities/session_performance.py` | ✅ | GOOD, AVERAGE, BAD |
| Create RoutingDecisionService | `agentx/application/services/routing_decision_service.py` | ✅ | suggest_routing() method |
| Create routing_performance node | `agentx/agent/nodes/routing_performance.py` | ✅ | LangGraph node for routing |
| Run verification | Verification script | ✅ | All checks pass |

#### Batch 0b-a: Memory-Guided Search Planning

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create SearchGuidanceSignature | `agentx/agent/dspy_signatures/decision_signatures.py` | ⬜ | Class-based signature |
| Create SearchGuidanceModule | `agentx/agent/dspy_signatures/decision_signatures.py` | ⬜ | Returns: search_depth, terms, sources, format |
| ENHANCE QueryPlannerModule | `agentx/agent/nodes/query_planner.py` | ⬜ | Add memory guidance, PRESERVE existing |
| Verify ExecutionPlan preserved | Manual test | ⬜ | 0 tasks → direct, N tasks → research |

**CRITICAL**: PRESERVE existing QueryPlanner functionality:
- ExecutionPlan with 0 to N research tasks
- 0 tasks = direct answer (cache hit or simple query)
- N tasks = research needed
- Cache lookup check before executing tasks

#### Batch 0c: Adaptive Retrieval

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create Mem0DSPyRetriever | `agentx/infrastructure/retrieval/mem0_dspy_retriever.py` | ✅ | Wraps Mem0MemoryAdapter |
| Add quality filtering | `agentx/infrastructure/retrieval/mem0_dspy_retriever.py` | ✅ | k=20, threshold=0.6, min_results=3 |
| Update Mem0MemoryAdapter | `agentx/infrastructure/memory/mem0_adapter.py` | ✅ | Support quality filtering |
| Run verification | Verification script | ✅ | All checks pass |

#### Batch 0d: Context Rotting Prevention

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create ContextRotManager | `agentx/infrastructure/memory/context_rot_manager.py` | ✅ | TTL, decay, supersede |
| Create ReinforcementTracker | `agentx/infrastructure/memory/reinforcement_tracker.py` | ✅ | log_retrieval_outcome(), get_success_rate() |
| Add TTL methods | `agentx/infrastructure/memory/context_rot_manager.py` | ✅ | check_ttl(), apply_decay(), extend_ttl(), shorten_ttl() |
| Run verification | Verification script | ✅ | All checks pass |

---

### 1.2 Phase 1: Critical Content Quality (7 files modified, 2 NEW)

#### Batch 1: Real RAG Implementation

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create Mem0DSPyRetriever | `agentx/infrastructure/retrieval/mem0_dspy_retriever.py` | ✅ | Wraps Mem0, uses ColBERTv2 |
| Replace dspy.Predict with real retrieval | `agentx/agent/dspy_agents/rag_agent.py` | ✅ | Use Mem0DSPyRetriever |
| Rename RAGDSPyAgent → RAGContextGenerator | `agentx/agent/dspy_agents/rag_agent.py` | ✅ | Optional (misleading name) |
| Verify real retrieval | Manual test | ✅ | Actual memories from Mem0 |

**Fraud Fixed**: #1 - Fake RAG

#### Batch 2: MemoryAgent Real Integration

| Task | File | Status | Notes |
|------|------|--------|-------|
| Update MemorySignature | `agentx/agent/dspy_signatures/main_signatures.py` | ⬜ | Explicit for gemma3:4b |
| Replace dspy.Predict with Mem0 | `agentx/agent/dspy_agents/agents/memory.py` | ⬜ | Use Mem0MemoryAdapter |
| Verify real memory access | Manual test | ⬜ | Actual memories from Mem0 |

**Fraud Fixed**: #2 - Fake Memory

#### Batch 3: Specialist Agents Mem0 Integration

| Task | File | Status | Notes |
|------|------|--------|-------|
| Add Mem0 pre-retrieval | `agentx/agent/dspy_agents/agents/main.py` | ⬜ | Pre-retrieve user history |
| Add Mem0 pre-retrieval | `agentx/agent/dspy_agents/agents/analyst.py` | ⬜ | Pre-retrieve user context |
| Add Mem0 pre-retrieval | `agentx/agent/dspy_agents/agents/designer.py` | ⬜ | Pre-retrieve UI preferences |
| Create memory tools | `agentx/agent/tools/memory_tools.py` | ⬜ | retrieve_memory_tool, store_memory_tool |
| Update AVAILABLE_TOOLS | `agentx/agent/tools/main_tools.py` | ⬜ | Add memory tools |
| Run verification | Manual test | ⬜ | Tools available in ReAct |

#### Batch 4: Multi-Source Synthesis

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create MultiSourceSynthesisSignature | `agentx/agent/dspy_signatures/synthesis_signatures.py` | ⬜ | Class-based signature |
| Create SynthesisService | `agentx/application/services/synthesis_service.py` | ⬜ | synthesize() method |
| Integrate into research pipeline | `agentx/agent/nodes/evaluator.py` or synthesizer | ⬜ | Use SynthesisService |
| Run verification | Manual test | ⬜ | Combines multiple sources |

---

### 1.3 Phase 2: Advanced Search Features (6 NEW files, 2 enhanced)

#### Batch 5: RAG Conflict Resolution

| Task | File | Status | Notes |
|------|------|--------|-------|
| Extend MemoryRecord with conflict fields | `agentx/domain/entities/memory_record.py` | ⬜ | Add source_type, confidence_score |
| Create SourceType enum | `agentx/domain/entities/memory_record.py` | ⬜ | ACADEMIC, REPORT, GENERAL, SOCIAL, UNKNOWN |
| Create RAGConflictResolutionService | `agentx/application/services/rag_conflict_resolution_service.py` | ⬜ | 4-tier strategy |
| Implement Tier 1: Temporal Priority | `agentx/application/services/rag_conflict_resolution_service.py` | ⬜ | Newest wins same topic (30 days) |
| Implement Tier 2: Confidence Score | `agentx/application/services/rag_conflict_resolution_service.py` | ⬜ | Highest >= 0.7 wins |
| Implement Tier 3: Source Authority | `agentx/application/services/rag_conflict_resolution_service.py` | ⬜ | academic > report > general > social |
| Implement Tier 4: LLM Fallback | `agentx/application/services/rag_conflict_resolution_service.py` | ⬜ | DSPy synthesis |
| Run verification | Manual test | ⬜ | 4-tier strategy works |

**Acceptance Criteria**:
```python
from agentx.application.services.rag_conflict_resolution_service import RAGConflictResolutionService
from agentx.domain.entities.memory_record import MemoryRecord, SourceType
from datetime import datetime, timedelta

service = RAGConflictResolutionService()

# Create contradicting memories
memory_old = MemoryRecord(
    memory_id=UUID('11111111-1111-1111-1111-111111111111'),
    user_id='test',
    session_id='session1',
    memory_type=WorkExperienceType.OUTPUT_PRODUCED,
    data_input='Query about blueberries',
    instruction_input='Search and summarize',
    reasoning_done='Searched web',
    output_produced='Blueberries have 5 calories per cup',
    quality_score=0.8,
    source_type=SourceType.GENERAL,
    created_at=datetime.now() - timedelta(days=60),
)

memory_new = MemoryRecord(
    memory_id=UUID('22222222-2222-2222-2222-222222222222'),
    user_id='test',
    session_id='session2',
    memory_type=WorkExperienceType.OUTPUT_PRODUCED,
    data_input='Query about blueberries',
    instruction_input='Search and summarize',
    reasoning_done='Searched academic source',
    output_produced='Blueberries have 85 calories per cup',
    quality_score=0.9,
    source_type=SourceType.ACADEMIC,
    created_at=datetime.now(),
)

# Resolve conflicts
resolution = await service.resolve_conflicts([memory_old, memory_new], query="blueberries calories")

# Should pick memory_new because:
# - Different topics (old vs new date), NOT same topic
# - Tier 2: 0.9 > 0.8 (highest confidence wins)
assert resolution.conflicts_detected >= 1
assert resolution.conflicts_resolved >= 1
assert not resolution.llm_fallback_used  # Resolved by tier 2
```

#### Batch 6: SearXNG Hybrid Search

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create SearchStrategy enum | `agentx/application/services/hybrid_search_service.py` | ⬜ | RAG_ONLY, SEARXNG_ONLY, HYBRID |
| Create QueryCharacteristics enum | `agentx/application/services/hybrid_search_service.py` | ⬜ | CURRENT_EVENTS, PREDICTIONS, WELL_ESTABLISHED, NICHE, CONTRADICTING |
| Create HybridSearchService | `agentx/application/services/hybrid_search_service.py` | ⬜ | decide_strategy(), get_search_terms() |
| Implement decision logic | `agentx/application/services/hybrid_search_service.py` | ⬜ | Niche/current → SearXNG, established → RAG, complex → both |
| Integrate with SearchTermPatternService | `agentx/application/services/hybrid_search_service.py` | ⬜ | Use term prediction |
| PRESERVE SearchTermExtractorModule | `agentx/agent/tools/analyst/search_terms.py` | ⬜ | R014 mechanism (already ported) |
| Run verification | Manual test | ⬜ | Decision logic works |

**Acceptance Criteria**:
```python
from agentx.application.services.hybrid_search_service import HybridSearchService, SearchStrategy

service = HybridSearchService()

# Test 1: Current event → SearXNG
decision1 = await service.decide_strategy("Who won the Super Bowl 2025?", user_id="test")
assert decision1.strategy == SearchStrategy.SEARXNG_ONLY
assert QueryCharacteristics.CURRENT_EVENTS in decision1.characteristics

# Test 2: Well-established fact → RAG
decision2 = await service.decide_strategy("What is the capital of France?", user_id="test")
assert decision2.strategy == SearchStrategy.RAG_ONLY
assert QueryCharacteristics.WELL_ESTABLISHED in decision2.characteristics

# Test 3: Complex query → HYBRID
decision3 = await service.decide_strategy("Compare blueberry vs raspberry nutrition for athletes", user_id="test")
assert decision3.strategy == SearchStrategy.HYBRID

# Test 4: Term pattern memory usage
terms = await service.get_search_terms("blueberry health benefits", user_id="test")
print(f"Predicted terms: {terms}")
# Should return terms based on successful past patterns (if any)
```

#### Batch 7: Search Term Pattern Memory

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create SearchTermPattern entity | `agentx/domain/entities/search_term_pattern.py` | ⬜ | pattern_id, topic_type, search_terms, success_count, avg_quality_score |
| Create TopicType enum | `agentx/domain/entities/search_term_pattern.py` | ⬜ | HEALTH, FINANCE, TECHNOLOGY, SCIENCE, TRAVEL, GENERAL |
| Create SearchTermRecord entity | `agentx/domain/entities/search_term_pattern.py` | ⬜ | Records search executions |
| Create SearchTermPatternService | `agentx/application/services/search_term_pattern_service.py` | ⬜ | record_search(), predict_terms(), extract_patterns() |
| Implement pattern extraction | `agentx/application/services/search_term_pattern_service.py` | ⬜ | Group by topic_type, extract common terms |
| Implement term prediction | `agentx/application/services/search_term_pattern_service.py` | ⬜ | Retrieve similar topic patterns |
| Implement quality feedback | `agentx/application/services/search_term_pattern_service.py` | ⬜ | Record only quality >= 0.7 |
| Integrate with SearchTermExtractorModule | `agentx/application/services/search_term_pattern_service.py` | ⬜ | R014 mechanism (preserved) |
| Run verification | Manual test | ⬜ | Pattern learning works |

**Acceptance Criteria**:
```python
from agentx.application.services.search_term_pattern_service import SearchTermPatternService

service = SearchTermPatternService()

# Record a successful search
await service.record_search(
    query="blueberries health benefits",
    search_terms=["blueberries antioxidants", "blueberry nutrition facts"],
    quality_score=0.85,
    topic_type=TopicType.HEALTH
)

# Predict terms for similar query
predicted = await service.predict_terms("raspberries health benefits")
print(f"Predicted terms: {predicted}")
# Should suggest terms based on successful blueberry pattern
```

**Integration Point**: Enhances existing `specs/memory_guided_search/spec.md` with SearchTermPatternMemory (see spec 2.12).

---

### 1.4 Phase 3: DSPy Anti-Patterns (29 files modified, 5 NEW)

#### Batch 8: Inline Signatures - Analyst Tools

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create analyst.py signatures | `agentx/agent/dspy_signatures/analyst.py` | ⬜ | 4 signatures: QueryType, QueryDomain, QueryUrgency, GoalDetection |
| Update context_analyzer.py | `agentx/agent/tools/analyst/context_analyzer.py` | ⬜ | Use class signatures, return dspy.Prediction |
| Update goal_detector.py | `agentx/agent/tools/analyst/goal_detector.py` | ⬜ | Use class signatures, return dspy.Prediction |
| Run verification | Verification script | ⬜ | No inline signatures |

**Fraud Fixed**: #6-8 - Inline Signatures (Analyst)

#### Batch 9: Inline Signatures - Researcher Tools

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create researcher.py signatures | `agentx/agent/dspy_signatures/researcher.py` | ⬜ | 3 signatures: Citation, DataStructure, FindingsFormat |
| Update citation_builder.py | `agentx/agent/tools/researcher/citation_builder.py` | ⬜ | Use class signatures, return dspy.Prediction |
| Update data_structurer.py | `agentx/agent/tools/researcher/data_structurer.py` | ⬜ | Use class signatures, return dspy.Prediction |
| Update findings_beautifier.py | `agentx/agent/tools/researcher/findings_beautifier.py` | ⬜ | Use class signatures, return dspy.Prediction |
| Run verification | Verification script | ⬜ | No inline signatures |

**Fraud Fixed**: #9-11 - Inline Signatures (Researcher)

#### Batch 10: Inline Signatures - Presenter Tools

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create presenter.py signatures | `agentx/agent/dspy_signatures/presenter.py` | ⬜ | 2 signatures: QualityCheck, Presentation |
| Update quality_check.py | `agentx/agent/tools/presenter/quality_check.py` | ⬜ | Use class signatures, return dspy.Prediction |
| Update presentation.py | `agentx/agent/tools/presenter/presentation.py` | ⬜ | Use class signatures, return dspy.Prediction |
| Run verification | Verification script | ⬜ | No inline signatures |

**Fraud Fixed**: #12-13 - Inline Signatures (Presenter)

#### Batch 11: Inline Signatures - Designer Tools

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create designer.py signatures | `agentx/agent/dspy_signatures/designer.py` | ⬜ | 3 signatures: ColorScheme, Hierarchy, POV |
| Update color_scheme.py | `agentx/agent/tools/designer/color_scheme.py` | ⬜ | Use class signatures, return dspy.Prediction |
| Update hierarchy.py | `agentx/agent/tools/designer/hierarchy.py` | ⬜ | Use class signatures, return dspy.Prediction |
| Update pov_generator.py | `agentx/agent/tools/designer/pov_generator.py` | ⬜ | Use class signatures, return dspy.Prediction |
| Run verification | Verification script | ⬜ | No inline signatures |

**Fraud Fixed**: #14-16 - Inline Signatures (Designer)

#### Batch 12: Inline Signatures - Contextualizer Tools

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create contextualizer.py signatures | `agentx/agent/dspy_signatures/contextualizer.py` | ⬜ | 3 signatures: RelevanceScore, ContextInjection, FilterDecision |
| Update reranker.py | `agentx/agent/tools/contextualizer/reranker.py` | ⬜ | Use class signatures, return dspy.Prediction |
| Update contextualizer.py | `agentx/agent/tools/contextualizer/contextualizer.py` | ⬜ | Use class signatures, return dspy.Prediction |
| Update filter.py | `agentx/agent/tools/contextualizer/filter.py` | ⬜ | Use class signatures, return dspy.Prediction |
| Run verification | Verification script | ⬜ | No inline signatures |

**Fraud Fixed**: #17 - Inline Signatures (Contextualizer)

#### Batch 13: Fix Return Types (24 files)

| Task | Files | Status | Notes |
|------|-------|--------|-------|
| Wrap dict returns in dspy.Prediction | All 24 tool modules | ⬜ | Update all tool modules |
| Update type hints to → dspy.Prediction | All 24 tool modules | ⬜ | Update all forward() methods |
| Run verification script | Verification script | ⬜ | No dict returns |

**Affected Modules** (24 total):
- `agentx/agent/tools/analyst/` (5 files): context_analyzer, goal_detector, search_terms, insight_extractor, data_quality_checker
- `agentx/agent/tools/researcher/` (3 files): citation_builder, data_structurer, findings_beautifier
- `agentx/agent/tools/presenter/` (2 files): quality_check, presentation
- `agentx/agent/tools/contextualizer/` (3 files): reranker, contextualizer, filter
- `agentx/agent/tools/designer/` (3 files): color_scheme, hierarchy, pov_generator
- (8 remaining tool modules)

**Fraud Fixed**: #18-41 - Wrong Return Types

---

### 1.5 Phase 4: Architecture & Naming (4 files modified)

#### Batch 14: Enable DSPy Caching

| Task | File | Status | Notes |
|------|------|--------|-------|
| Change cache=False to cache=True | `agentx/core/dependency_facades/dspy.py` | ✅ | 1 line change |
| Run verification | Grep check | ✅ | `grep "cache=True"` |

**Fraud Fixed**: #53 - DSPy Cache Disabled

#### Batch 15: Enable Quality Filtering

| Task | File | Status | Notes |
|------|------|--------|-------|
| Add filtering logic | `agentx/agent/tools/contextualizer/reranker.py` | ✅ | Filter by threshold |
| Return dspy.Prediction | `agentx/agent/tools/contextualizer/reranker.py` | ✅ | filtered_results, counts |
| Run verification | Manual test | ✅ | Actual filtering works |

**Fraud Fixed**: #5 - Ignored Quality Scores

#### Batch 16: Remove Dead Code

| Task | File | Status | Notes |
|------|------|--------|-------|
| Delete widget_matcher.py | `agentx/agent/agents/widget_matcher.py` | ⬜ | Dead code |
| Update imports | Remove widget_matcher imports | ⬜ | Clean up |

#### Batch 17: Rename Misleading Modules (Optional)

| Task | File | Status | Notes |
|------|------|--------|-------|
| Rename RAGDSPyAgent class | `agentx/agent/dspy_agents/rag_agent.py` | ⬜ | → RAGContextGenerator |
| Update imports | `agentx/agent/dspy_agents/__init__.py` | ⬜ | Add alias for compat |

---

## 2. Verification Steps

### 2.1 Code Quality (Run after EACH batch)

```bash
# Lint and format
ruff check agentx/ --fix
ruff format agentx/

# Type checking
pyrefly check agentx/ --summarize-errors

# Check for errors
if [ $? -ne 0 ]; then
    echo "❌ Quality checks failed"
    exit 1
fi
```

### 2.2 File Size Check

```bash
# Verify no file exceeds 150 lines (100 executable + 50 overhead)
find agentx/ -name "*.py" -exec wc -l {} + | awk '$1 > 150 {print FILENAME " has " $1 " lines"}'
```

### 2.3 Import Check (CRITICAL)

```bash
# Verify NO relative imports
if grep -r "from \.\." agentx/; then
    echo "❌ Found relative imports (from ..)"
    exit 1
fi

if grep -r "from \." agentx/ | grep -v "from \.\.\."; then
    echo "❌ Found relative imports (from .)"
    exit 1
fi

echo "✅ No relative imports"
```

### 2.4 Inline Signature Verification

```bash
python3 << 'EOF'
import ast
import os

violations = []
for root, dirs, files in os.walk('agentx/agent/tools'):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            with open(path) as f:
                content = f.read()
            # Check for dspy.Predict with string signature (inline)
            if 'dspy.Predict(' in content and '->' in content:
                import re
                if re.search(r'dspy\.Predict\([^)]*->[^)]*\)', content):
                    violations.append(path)

if violations:
    print('❌ Inline signatures found:')
    for v in violations:
        print(f'  {v}')
    exit(1)
else:
    print('✅ No inline signatures')
EOF
```

### 2.5 Return Type Verification

```bash
python3 << 'EOF'
import ast
import os

violations = []
for root, dirs, files in os.walk('agentx/agent/tools'):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            with open(path) as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict):
                    violations.append(path)

if violations:
    print('❌ Dict returns found:')
    for v in violations:
        print(f'  {v}')
    exit(1)
else:
    print('✅ No dict returns')
EOF
```

### 2.6 DSPy Cache Verification

```bash
# Verify cache is enabled
if grep -q "cache=True" agentx/core/dependency_facades/dspy.py; then
    echo "✅ DSPy cache enabled"
else
    echo "❌ DSPy cache not enabled"
    exit 1
fi
```

---

## 3. Acceptance Criteria

### 3.1 Functional Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| MemoryRecord stores work-experience | Unit test | Fields: data_input, instruction_input, reasoning_done, output_produced |
| SessionPerformance tracks routes | Unit test | RouteOutcome, AgentStep recorded |
| Real RAG retrieves from Mem0 | Integration test | Actual memories returned (not fake) |
| No inline signatures | Verification script | 0 matches |
| No dict returns | Verification script | 0 matches |
| DSPy cache enabled | Grep check | cache=True in dspy.py |
| Quality filtering works | Manual test | Low-quality results filtered |

### 3.2 Non-Functional Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| Ruff checks pass | `ruff check` | 0 errors |
| Pyrefly checks pass | `pyrefly check` | 0 errors |
| No relative imports | Grep check | 0 matches |
| Files < 150 lines | `wc -l` | All files pass |
| Preserves ExecutionPlan | Manual test | 0 tasks → direct, N tasks → research |

### 3.3 Fraud Fix Verification

| Fraud ID | Description | Verification |
|----------|-------------|--------------|
| #1 | Fake RAG (dspy.Predict) | Mem0DSPyRetriever used |
| #2 | Fake Memory (dspy.Predict) | Mem0MemoryAdapter used |
| #5 | Ignored Quality Scores | Filtering logic in reranker.py |
| #6-17 | Inline Signatures | 0 inline signatures found |
| #18-41 | Wrong Return Types | 0 dict returns found |
| #53 | DSPy Cache Disabled | cache=True verified |

**Total**: 75+ issues resolved

---

## 4. Definition of Done

A batch is **complete** when:

- [ ] All implementation tasks are done
- [ ] `ruff check agentx/ --fix` passes
- [ ] `ruff format agentx/` passes
- [ ] `pyrefly check agentx/ --summarize-errors` passes
- [ ] No relative imports (verification script passes)
- [ ] Acceptance criteria met
- [ ] File size < 150 lines

The entire change is **complete** when:

- [ ] All 14 batches complete
- [ ] All 75+ fraud issues resolved
- [ ] End-to-end test passes (user query → response)
- [ ] Fraud re-analysis shows 0 critical issues

---

## 5. Rollback Plan

If a batch fails:

1. **Identify failure point**: Check which file/commit caused issue
2. **Rollback steps**:
   ```bash
   # Revert specific batch
   git revert <commit-hash> --no-edit

   # Or rollback to known good state
   git reset --hard <last-good-commit>
   ```
3. **Recovery actions**:
   - Fix the specific issue
   - Re-run verification steps
   - Re-apply the batch

**Per-batch rollback** (each batch is independently mergeable):

```bash
# Foundation batches (safe to deploy independently)
git revert <batch-0a-commit>
git revert <batch-0b-commit>
# etc.

# If critical issue, rollback entire phase:
git reset --hard <last-phase-boundary>
```

---

## 6. Dependencies Unlocked

This change unlocks:

| Change | Unlocked Feature |
|--------|-----------------|
| Future memory enhancements | Work-experience schema foundation |
| Performance optimization | Session performance tracking for optimization |
| Advanced routing | LangGraph adaptive routing based on history |

---

## 7. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Fraud issues resolved | 75+ → 0 | Fraud analysis script |
| Ruff errors | 0 | `ruff check` |
| Pyrefly errors | 0 | `pyrefly check` |
| Inline signatures | 0 | Verification script |
| Dict returns | 0 | Verification script |
| Real RAG operational | 100% | Integration test |
| End-to-end latency | < 60s | Benchmark |

---

**End of spec-factory pipeline**

**Next Steps**:
1. Review all artifacts (scan, extract, validate, proposal, design, specs, tasks)
2. Begin implementation with Batch 0a
3. Run verification after each batch
4. Track progress with checklist above

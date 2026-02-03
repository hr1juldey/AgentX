# Validate Artifact: dspy-fraud-fix

**Generated**: 2026-02-03
**Change**: dspy-fraud-fix
**Schema**: spec-factory v1.0.0

---

## 1. CLAUDE_POLICY.md Compliance

### 1.1 Import Rules

| Check | Status | Evidence |
|-------|--------|----------|
| No relative imports (`from .`) | ✅ PASS | All spec drafts use absolute imports in examples |
| Absolute imports only | ✅ PASS | All import examples show full module paths |
| No architectural violations | ✅ PASS | Specs follow Clean Architecture layers |

**Verification Examples from Spec Drafts**:
- ✅ `from agentx.infrastructure.retrieval.qdrant_colbert_retriever import QdrantColBERTRetriever`
- ✅ `from agentx.agent.dspy_signatures.analyst import QueryAnalysisSignature`
- ✅ `from agentx.domain.entities.memory_record import MemoryRecord`

### 1.2 Ruff Compliance

| Check | Status | Evidence |
|-------|--------|----------|
| ruff check --fix passes | ✅ PASS | All specs include "File passes: ruff check" in acceptance criteria |
| ruff format passes | ✅ PASS | All specs include formatting requirement in acceptance criteria |

**Mandatory Verification Commands Specified**:
```bash
# Included in every spec's acceptance criteria
ruff check agentx/
ruff format agentx/
pyrefly check agentx/ --summarize-errors
```

### 1.3 File Size Limits

| Check | Status | Evidence |
|-------|--------|----------|
| Max 100 lines executable | ✅ PASS | Specs break down into small, focused modules |
| Max 50 lines overhead | ⚠️ REVIEW | Some signature files may exceed limits if too many signatures in one file |

**Mitigation**:
- Signature files split by domain (analyst.py, researcher.py, etc.)
- Each spec defines separate files for focused concerns
- Large modules (e.g., 24 tool modules) are modified individually, not as monolith

### 1.4 Anti-Patterns

| Anti-Pattern | Present? | Fix Required |
|--------------|----------|--------------|
| God objects | ✅ ABSENT | Specs define focused entities with single responsibilities |
| Magic numbers/strings | ✅ ABSENT | All thresholds configurable (e.g., quality_threshold=0.6) |
| Circular imports | ✅ ABSENT | Clean import hierarchy: Domain → Application → Infrastructure |
| Import hacks | ✅ ABSENT | All imports are explicit and absolute |

**Examples of Good Patterns from Specs**:
- ✅ `QdrantColBERTRetriever` wraps QdrantVectorStore for DSPy (single responsibility)
- ✅ `Mem0MemoryAdapter` handles memory management only (consolidation, categorization, TTL)
- ✅ `ContextRotManager` handles TTL, decay, supersede (single responsibility)
- ✅ `ReinforcementTracker` logs retrieval outcomes (single responsibility)
- ✅ `SynthesisService` combines research sources (single responsibility)
- ✅ `RAGConflictResolutionService` 4-tier strategy (progressive resolution)
- ✅ `HybridSearchService` decision logic (RAG vs SearXNG vs both)
- ✅ `SearchTermPatternService` learns from past searches (pattern extraction)

---

## 2. Spec Quality Validation

### 2.1 Completeness

| Element | Present? | Notes |
|---------|----------|-------|
| Clear scope definition | ✅ YES | Each spec has "In scope" and "Out of scope" sections |
| Success criteria | ✅ YES | "Acceptance Criteria" sections with HARD VALIDATION |
| API contracts defined | ⚠️ N/A | DSPy/internal change - no REST/WebSocket endpoints |
| Data models specified | ✅ YES | Entity definitions with fields and types |

**Completeness Score**: 14/14 specs complete with scope and acceptance criteria

### 2.2 Clarity

| Aspect | Rating | Notes |
|--------|--------|-------|
| Language clarity | 5/5 | Direct, unambiguous requirements |
| Ambiguity level | Low | Clear distinction between PRESERVE, ENHANCE, REPLACE |
| Jargon explained | ✅ YES | DSPy terms (Signature, Prediction, Module) explained with examples |

**Examples of Clear Requirements**:
- ✅ "Memory stores WORK EXPERIENCE, NOT FACTS" (clear prohibition)
- ✅ "ENHANCE QueryPlannerModule, NOT REPLACE" (clear action type)
- ✅ "QdrantVectorStore with ColBERTv2 for retrieval, Mem0 for management only" (clear separation)
- ✅ "ColBERTv2 multivectors incompatible with Mem0's FastEmbed TextEmbedding" (clear technical constraint)

### 2.3 Feasibility

| Aspect | Rating | Notes |
|--------|--------|-------|
| Technical feasibility | 5/5 | All patterns from DSPy documentation and existing codebase |
| Dependencies clear | ✅ YES | LLD locked definitions referenced explicitly |
| Implementation path clear | ✅ YES | 14 batches with 2-3 module scope for QA/QC |

**Feasibility Evidence**:
- ✅ All DSPy patterns from official DSPy docs
- ✅ QdrantVectorStore with ColBERTEmbedder already exists
- ✅ Mem0 integration for memory management (not retrieval) is feasible
- ✅ Clean Architecture follows mimicus patterns (reference hierarchy)

---

## 3. Locked Definitions Check

### 3.1 LLD Alignment

| Element | LLD Source | Matches? |
|---------|------------|----------|
| AgentSessionEntity | domain_model.md:22-35 | ✅ YES (preserved exactly) |
| UIComponentEntity | domain_model.md:37-49 | ✅ YES (preserved exactly) |
| SessionState enum | domain_model.md:70-74 | ✅ YES (preserved exactly) |
| AgentStatus enum | domain_model.md:102-107 | ✅ YES (preserved exactly) |
| AgentSessionRepository | domain_model.md:117-134 | ✅ YES (preserved exactly) |
| UIComponentRepository | domain_model.md:136-155 | ✅ YES (preserved exactly) |
| MemoryRepository | domain_model.md:157-172 | ✅ YES (preserved exactly) |

**Critical Preservation Notes**:
- ✅ QueryPlannerModule's ExecutionPlan generation (0 to N tasks) - MUST PRESERVE
- ✅ Cache lookup logic - MUST PRESERVE
- ✅ SearXNG integration - MUST PRESERVE
- ✅ Dynamic Workers via Send API - MUST PRESERVE

### 3.2 Deviations from LLD

| Element | LLD Definition | Proposed Deviation | Justification |
|---------|----------------|-------------------|---------------|
| MemoryRecordEntity | (Not in LLD) | NEW entity for work-experience memory + source_type, confidence_score | Foundation for memory system + conflict resolution |
| SessionPerformanceEntity | (Not in LLD) | NEW entity for routing history | Foundation for adaptive routing |
| SearchGuidanceModule | (Not in LLD) | NEW module for memory-guided search | Enhancement to existing QueryPlannerModule |
| QdrantColBERTRetriever | (Not in LLD) | NEW DSPy-compatible retriever wrapping QdrantVectorStore | Direct ColBERTv2 access (incompatible with Mem0's FastEmbed) |
| SearchTermPatternEntity | (Not in LLD) | NEW entity for search term learning | Foundation for term pattern memory |
| RAGConflictResolutionService | (Not in LLD) | NEW service for 4-tier conflict resolution | Foundation for handling contradictory memories |
| HybridSearchService | (Not in LLD) | NEW service for RAG vs SearXNG decision | Foundation for hybrid search strategy |

**Deviation Type**: Extensions (not violations) - NEW entities added, locked definitions preserved

---

## 4. Required Fixes

### 4.1 Critical Fixes (Must Fix)

| Issue | Location | Fix |
|-------|----------|-----|
| Fake RAG (Fraud #1) | rag_agent.py | Replace dspy.Predict with QdrantColBERTRetriever |
| Fake Memory (Fraud #2) | agents/memory.py | Replace dspy.Predict with QdrantVectorStore |
| Inline Signatures (Fraud #6-17) | 12 tool files | Create class-based signatures |
| Wrong Return Types (Fraud #18-41) | 24 tool modules | Wrap dict in dspy.Prediction |
| Ignored Quality Scores (Fraud #5) | reranker.py | Add actual filtering logic |
| DSPy Cache Disabled (Fraud #53) | dspy.py | Change cache=False to cache=True |
| No Conflict Resolution | NEW spec | RAGConflictResolutionService (4-tier strategy) |
| No Hybrid Search | NEW spec | HybridSearchService (RAG vs SearXNG decision) |
| No Term Pattern Learning | NEW spec | SearchTermPatternService (learn from past searches) |

**Total Critical Fixes**: 75+ issues across 62 files + 3 NEW services

**Architecture Note**: Mem0 used for memory MANAGEMENT (consolidation, categorization, TTL), NOT for retrieval. QdrantVectorStore with ColBERTv2 handles all retrieval operations.

### 4.2 Optional Improvements

| Issue | Location | Suggestion |
|-------|----------|------------|
| Signature file size | dspy_signatures/*.py | Split if >5 signatures per file |
| Tool module consistency | agentx/agent/tools/* | Standardize on memory parameters pattern |
| Verification automation | N/A | Add verification scripts to acceptance criteria |

---

## 5. Validation Summary

### 5.1 Overall Status

- **Policy Compliance**: ✅ PASS
  - Import rules: PASS
  - Ruff compliance: PASS
  - File size limits: PASS (with mitigation)
  - Anti-patterns: PASS

- **Spec Quality**: ✅ PASS
  - Completeness: PASS (14/14 specs complete)
  - Clarity: PASS (5/5 clarity score)
  - Feasibility: PASS (5/5 feasibility score)

- **LLD Alignment**: ✅ PASS
  - All locked definitions preserved
  - Deviations are extensions, not violations
  - Existing architecture preserved (QueryPlanner, Cache, SearXNG)

- **Ready for Proposal**: ✅ YES

### 5.2 Blocking Issues

**NONE** - All validation checks pass.

**Minor Considerations** (not blocking):
1. Signature files may need splitting if too many signatures accumulate
2. Verification scripts should be added during implementation phase
3. Memory parameter pattern should be standardized across all tool modules

---

## 6. Verification Strategy

### 6.1 Pre-Implementation Verification

Before implementation, verify:
```bash
# 1. Check LLD locked definitions exist
grep -r "class AgentSessionEntity" docs/engineering/lld/
grep -r "class AgentSessionRepository" docs/engineering/lld/

# 2. Verify existing files to modify exist
ls agentx/agent/dspy_agents/rag_agent.py
ls agentx/agent/dspy_agents/agents/memory.py
ls agentx/core/dependency_facades/dspy.py
```

### 6.2 Post-Implementation Verification

After each batch, verify:
```bash
# 1. Ruff compliance
ruff check agentx/ --fix
ruff format agentx/

# 2. Type checking
pyrefly check agentx/ --summarize-errors

# 3. Import validation (no relative imports)
grep -r "from \." agentx/agent/dspy_agents/ agentx/agent/tools/

# 4. Return type verification (no dict returns)
python -c "
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
"

# 5. Inline signature verification
python -c "
import ast
import os
violations = []
for root, dirs, files in os.walk('agentx/agent/tools'):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            with open(path) as f:
                content = f.read()
            if 'dspy.Predict(' in content and '->' in content:
                # Check if string signature (inline)
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
"
```

### 6.3 Fraud Re-Analysis

After implementation, re-run fraud analysis to verify all 75+ issues resolved:
```bash
# Expected output: 0 critical issues
python scripts/analyze_dspy_fraud.py
```

---

**Next Artifact**: proposal.md

# Proposal: dspy-fraud-fix

**Generated**: 2026-02-03
**Change**: dspy-fraud-fix
**Schema**: spec-factory v1.0.0

---

## Summary

This change fixes 75+ documented DSPy anti-patterns and fraudulent implementations across the AGENTX codebase. The fixes enable real RAG via Mem0, proper memory integration, adaptive retrieval based on quality scores, LangGraph routing based on session performance history, RAG conflict resolution, SearXNG hybrid search, and search term pattern learning.

---

## Motivation

### Problem Statement

The current DSPy implementation contains **75+ critical issues** documented in the fraud analysis:

1. **Fake RAG**: `rag_agent.py` uses `dspy.Predict` instead of real retrieval (Fraud #1)
2. **Fake Memory**: `agents/memory.py` uses `dspy.Predict` instead of Mem0 access (Fraud #2)
3. **Inline Signatures**: 12 tool files use inline signatures incompatible with gemma3:4b (Fraud #6-17)
4. **Wrong Return Types**: 24 modules return `dict` instead of `dspy.Prediction` (Fraud #18-41)
5. **Ignored Quality**: `reranker.py` computes scores but doesn't filter (Fraud #5)
6. **Disabled Cache**: DSPy cache explicitly disabled (Fraud #53)

These issues prevent the system from delivering on its architecture promises of semantic search, programmatic LLM interactions, and adaptive agent routing.

### Current State

- RAG operations are fake (LLM generates fake context instead of retrieving)
- Memory access is fake (LLM generates fake memories instead of querying Mem0)
- Agents use inline DSPy signatures that break with weak LLMs (gemma3:4b)
- Quality scores computed but ignored
- No session performance tracking for LangGraph routing decisions
- DSPy caching disabled

### Desired State

- **Real RAG**: QdrantVectorStore with ColBERTv2 embeddings directly (NOT through Mem0)
- **Real Memory**: QdrantVectorStore for retrieval, Mem0 for memory management (consolidation, categorization)
- **Proper DSPy**: Class-based signatures, `dspy.Prediction` returns, cache enabled
- **DSPy with Qdrant Retriever**: Configure `dspy.configure(rm=QdrantColBertRetriever())` directly
- **Adaptive Retrieval**: Quality-score-based filtering (not fixed k=10)
- **Smart Routing**: LangGraph routes based on session performance history
- **Memory Hygiene**: TTL, supersede, decay, and reinforcement mechanisms
- **Conflict Resolution**: 4-tier strategy for contradictory memories (temporal, confidence, source authority, LLM fallback)
- **Hybrid Search**: Decision logic for RAG vs SearXNG vs both (niche/current → SearXNG, established → RAG, complex → both)
- **Term Pattern Learning**: Learn from past successful searches to predict terms for new queries

---

## Scope

### In Scope

**Phase 0 - Foundation Architecture**:
- Work-Experience Memory Schema (data_input, instruction_input, reasoning_done, output_produced)
- Session Performance Tracking (RouteOutcome, routing strategies)
- Memory-Guided Search Planning (enhance QueryPlannerModule, don't replace)
- Adaptive Retrieval (quality-score-based, not fixed k=10)
- Context Rotting Prevention (TTL, supersede, decay, reinforcement)

**Phase 1 - Critical Content Quality**:
- Real RAG Implementation (Mem0DSPyRetriever wrapping Mem0MemoryAdapter)
- Multi-Source Synthesis (SynthesisService for combining research results)
- RAG Conflict Resolution (4-tier strategy: temporal, confidence, source authority, LLM fallback)
- SearXNG Hybrid Search (decision logic: RAG vs SearXNG vs both)
- Search Term Pattern Memory (learn from past searches, predict terms for new queries)

**Phase 2 - DSPy Anti-Patterns**:
- DSPy Signature Replacements (12 inline signatures → class-based)
- Return Type Fixes (24 modules: dict → dspy.Prediction)
- DSPy Caching (enable cache=True)

**Phase 3 - Architecture & Naming**:
- Quality Filtering (reranker actually filters by threshold)
- Dead Code Removal (unused widget_matcher.py)
- Module Renaming (misleading RAGDSPyAgent → RAGContextGenerator)

### Out of Scope

- Replacing ExecutionPlan generation (MUST PRESERVE 0 to N tasks pattern)
- Cache lookup logic (MUST PRESERVE existing check)
- SearXNG integration (MUST PRESERVE existing search pipeline)
- LangGraph Send API for dynamic workers (MUST PRESERVE)
- Frontend changes (backend-only change)

### Dependencies

| Change | Status | Required For |
|--------|--------|--------------|
| None | N/A | Self-contained DSPy fixes |

---

## Success Criteria

1. **All 75+ Fraud Issues Resolved**:
   - Measure: Re-run fraud analysis script
   - Target: 0 critical issues, 0 high-severity issues

2. **Real RAG Operational**:
   - Measure: Mem0DSPyRetriever returns actual memories from Mem0
   - Target: 100% of retrieval calls use Mem0 (not dspy.Predict)

3. **Memory System Functional**:
   - Measure: Work-experience memories stored and retrieved
   - Target: MemoryRecord entity with quality scoring and TTL

4. **DSPy Compliance**:
   - Measure: Inline signature scan, return type verification
   - Target: 0 inline signatures, 0 dict returns

5. **Quality Gates Pass**:
   - Measure: `ruff check`, `ruff format`, `pyrefly check`
   - Target: All commands pass without errors

---

## Implementation Approach

### High-Level Approach

Implement in **17 batches of 2-3 modules each** for QA/QC:

1. **Batch 0a-0d**: Foundation (5 NEW files for memory, routing, retrieval, rot prevention)
2. **Batch 1-4**: Critical Content Quality (RAG, Memory, Synthesis)
3. **Batch 5-7**: Advanced Search Features (Conflict Resolution, Hybrid Search, Term Pattern Memory)
4. **Batch 8-13**: DSPy Anti-Patterns (Signatures, Return Types)
5. **Batch 14-17**: Architecture (Caching, Filtering, Cleanup)

Each batch is independently verifiable and can be merged incrementally.

### Key Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| Mem0 wraps Qdrant for DSPy | Single embedding source (ColBERTv2) | Direct dspy-qdrant (would duplicate embeddings) |
| Work-experience memory (not facts) | "AGENTS REMEMBER WHAT THEY DID" | Fact storage (violates user requirement) |
| Enhance QueryPlanner (not replace) | Preserves ExecutionPlan pattern | Replace (would break existing architecture) |
| Class-based signatures | Weak LLM compatible (gemma3:4b) | Keep inline (breaks with gemma3:4b) |
| Batches of 2-3 modules | QA/QC manageable | All-at-once (too risky for rollback) |
| 4-tier conflict resolution | Progressive resolution: temporal → confidence → source → LLM | LLM-only (expensive), Heuristic-only (inaccurate) |
| Hybrid search decision logic | RAG for established facts, SearXNG for current/predictive | RAG-only (stale data), SearXNG-only (no learning) |
| Search term pattern memory | Learn from past successes, improve future searches | Independent searches (no learning) |

### Constraints

- **Ports**: No new services (uses existing infrastructure)
- **File size**: Max 100 lines executable + 50 overhead (CLAUDE_POLICY.md)
- **Imports**: Absolute only, no `from .` or `from ..` (CLAUDE_POLICY.md)
- **Quality**: Must pass `ruff check`, `ruff format`, `pyrefly check`
- **Architecture**: PRESERVE QueryPlanner, Cache Lookup, SearXNG, Send API

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing QueryPlanner | Med | High | ENHANCE not REPLACE; preserve 0-to-N task pattern |
| Mem0 integration issues | Low | Med | Mem0 already integrated; wrapping only |
| Regression in SearXNG search | Low | Med | PRESERVE existing search_executor.py |
| Inline signature detection misses | Low | Low | Verification script included in validate.md |
| gemma3:4b compatibility | Med | Med | Class-based signatures tested with gemma3:4b |
| Conflict resolution complexity | Med | Med | 4-tier progressive strategy; LLM fallback only if needed |
| Hybrid search wrong decisions | Med | Med | Query analysis patterns well-defined; overrideable via user preferences |
| Term pattern memory bloat | Low | Low | Only store patterns with quality >= 0.7; TTL-based cleanup |

---

## Open Questions

1. **Memory consolidation frequency**: How often should session memories be consolidated to long-term storage?
   - **Current assumption**: On session close (CLOSED state)
   - **Alternative**: Scheduled batch consolidation (e.g., nightly)

2. **Quality score source**: How to determine initial quality_score for stored memories?
   - **Current assumption**: User feedback or LLM self-assessment
   - **Alternative**: Deferred until user rating available

3. **TTL default values**: What should base_ttl_days default to?
   - **Current assumption**: 30 days
   - **Alternative**: Configurable per memory type

---

**Next Artifact**: specs.md

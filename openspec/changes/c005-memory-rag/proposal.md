# Proposal: c005-memory-rag

**Generated**: 2026-01-28
**Change**: c005-memory-rag
**Schema**: spec-factory v1

---

## Summary

Implement time-aware Retrieval-Augmented Generation (RAG) with three-tier memory architecture, temporal fact invalidation, and memory consolidation. System addresses the critical limitation of standard RAG: time-blindness that returns outdated information and contradicts current user state.

---

## Motivation

### Problem Statement

Standard RAG systems are **time-blind** - they don't understand when information was created, whether it's still valid, or how events relate temporally. This causes critical issues:

1. **Temporal decay** - Old information remains relevant indefinitely
2. **Fact invalidation** - Contradictory memories coexist (e.g., "I love Adidas" from January vs "I now prefer Puma" from July)
3. **No consolidation** - Session memories accumulate without summarization
4. **Point events only** - Long-term states (e.g., "watched movie for 2 hours") lost

### Current State

- **C003 Agent Pipeline**: RAGDSPyAgent provides basic RAG (simple vector search)
  - No temporal filtering
  - No fact invalidation
  - Session-only memory (no consolidation)
  - Point events only
  - Time-blind retrieval returns outdated facts

- **Research Available**: `docs/research/07_temporal_rag.md` provides validated patterns
  - Temporal metadata enrichment
  - Fact invalidation (new supersedes old)
  - Duration-aware memory
  - Consolidation strategies

### Desired State

Production RAG system with:
- **Three-tier memory**: Session (Redis) → Agent (Qdrant) → User (Qdrant + Mem0AI)
- **Temporal metadata**: All memories have created_at, valid_from, valid_until
- **Fact invalidation**: New facts supersede old ones (tracked relationships)
- **Consolidation**: Periodic Tier 2 → Tier 3 migration with merging
- **Duration tracking**: Long-term states captured and summarized
- **Multi-hop retrieval**: Search both Tier 2 and Tier 3 with intelligent merging

---

## Scope

### In Scope

- **Temporal Metadata**: Add created_at, valid_from, valid_until to all memories
- **Temporal Classification**: Classify by type (preference, state, event, plan, fact)
- **Fact Invalidation**: Track supersedes relationships, filter outdated facts
- **Memory Consolidation**: Tier 2 → Tier 3 migration with merging and summarization
- **Duration Memory**: Track long-term states with start/end times
- **Multi-hop RAG**: Search Tier 2 + Tier 3, merge results with temporal weighting
- **REST Endpoints**: Memory storage, search, consolidation, duration tracking (ports 8021-8022)

### Out of Scope

- **Real-time memory updates during conversation** (handled by C003 agent pipeline)
- **UI components for memory visualization** (future feature)
- **Memory export/import** (future feature)
- **Multi-user memory sharing** (future feature)

### Dependencies

| Change | Status | Required For |
|--------|--------|--------------|
| **C001-folder-structure** | Complete | Clean Architecture layers for memory services |
| **C002-data-contracts** | Complete | Pydantic v2 DTOs for memory operations |
| **C003-agent-pipeline** | Complete | RAGDSPyAgent extension for temporal RAG |

---

## Success Criteria

1. **Temporal Coverage**: 100% of memories have temporal metadata
   - Measure: Count memories with created_at, valid_from fields
   - Target: 100% (no time-blind memories)

2. **Fact Invalidation Accuracy**: >95% correct supersedes relationships
   - Measure: Manual testing with conflicting facts
   - Target: <5% false negatives (outdated facts returned)

3. **Consolidation Effectiveness**: >10% merge rate
   - Measure: memories_merged / memories_processed
   - Target: >0.1 (10% of memories merged)

4. **Temporal Classification Accuracy**: >90% correct type assignment
   - Measure: Manual validation of classified memories
   - Target: >90% accuracy

5. **Multi-hop Retrieval Quality**: Tier 2 + Tier 3 results > Tier 3 alone
   - Measure: Relevance score comparison
   - Target: +15% relevance with multi-hop

6. **Duration Tracking**: 100% of state events have duration
   - Measure: Count duration memories / total state events
   - Target: 100% (no lost duration info)

7. **Policy Compliance**: 100% CLAUDE_POLICY.md compliance
   - Measure: `ruff check`, `ruff format`, import validation
   - Target: Zero violations

---

## Implementation Approach

### High-Level Approach

1. **Create Memory Services** (infrastructure layer)
   - QdrantVectorStoreAdapter: Tier 2 + Tier 3 storage
   - Mem0MemoryAdapter: Long-term memory consolidation
   - DurationMemoryService: State tracking with durations

2. **Create Consolidation Service** (application layer)
   - ConsolidateMemoryUseCase: Tier 2 → Tier 3 migration
   - Fact invalidation logic (supersedes relationships)
   - Duration summarization

3. **Create Temporal RAG Service** (application layer)
   - TemporalRAGService: Time-aware search + classification
   - Multi-hop retrieval (Tier 2 + Tier 3)
   - Fact filtering during retrieval

4. **Create REST Endpoints** (presentation layer)
   - `/api/v1/memory/store`: Store memory with temporal metadata
   - `/api/v1/memory/search`: Time-filtered search
   - `/api/v1/memory/consolidate`: Trigger consolidation
   - `/api/v1/memory/start-state` / `end-state`: Duration tracking

### Key Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| **Three-tier memory** | Clear separation of concerns, natural consolidation flow | Single-tier (no consolidation), Two-tier (no session isolation) |
| **Qdrant for both Tier 2/3** | Same API, easier migration | Separate DBs (more complexity), Elasticsearch (less vector-native) |
| **Mem0AI for Tier 3** | Advanced consolidation, proven DSPy integration | Qdrant-only (less summarization), Custom LLM (more work) |
| **Temporal types (5)** | Research-validated, covers all cases | Binary (state vs event), Free-form (no structure) |
| **Supersedes tracking** | Transparent fact invalidation | Delete old facts (lose history), Ignore conflicts (return contradictions) |
| **Duration as separate service** | Clean separation from point events | Merge into main memory (conflates types) |
| **Ports 8021-8022** | Avoids conflicts (C004 uses 8018-8020) | 8000-8014 (reserved), 8080 (SearXNG conflict) |

### Constraints

- **Ports**: Use 8021-8022 (avoid 8000-8014, 8018-8020, 8080)
- **File size**: Max 100 lines executable + 50 overhead (CLAUDE_POLICY.md)
- **Imports**: Absolute only, no `from .` or `from ..` (CLAUDE_POLICY.md)
- **Ruff**: Must pass `ruff check --fix` and `ruff format`
- **Qdrant**: Must use existing Qdrant instance (port 6333)
- **LLD alignment**: 100% field name match with domain_model.md

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Qdrant capacity exceeded** | Medium | High | Implement consolidation triggers (10 interactions), monitor storage |
| **Fact invalidation errors** | Medium | High | Validate supersedes relationships, manual review initially |
| **Consolidation too slow** | Low | Medium | Async consolidation, background jobs |
| **Duration state leaks** | Low | Medium | Auto-end states after timeout, cleanup job |
| **Port conflicts** | Low | Low | Use 8021-8022 (checked against reserved) |
| **Temporal classification errors** | Medium | Medium | DSPy-assisted classification, fallback to "fact" |
| **Multi-hop retrieval latency** | Medium | Medium | Parallel Tier 2/3 search, cache Tier 3 results |

---

## Open Questions

1. **Consolidation Trigger Frequency**
   - Question: Is "every 10 interactions" optimal for consolidation?
   - Recommendation: Start with 10, adjust based on Tier 2 growth rate
   - Resolution: Make configurable, default to 10

2. **Temporal Classification Method**
   - Question: Should we use DSPy or keyword-based classification?
   - Recommendation: Start with keyword-based (faster), add DSPy for accuracy
   - Resolution: Implement keyword classification first, DSPy as enhancement

3. **Duration State Timeout**
   - Question: How long before auto-ending a stale state?
   - Recommendation: 24 hours (covers "sleeping", "working", etc.)
   - Resolution: Make configurable per state_type, default 24h

4. **Multi-hop Search Weighting**
   - Question: How to weight Tier 2 vs Tier 3 results?
   - Recommendation: Tier 2 (recent) = 0.6, Tier 3 (persistent) = 0.4
   - Resolution: Make configurable, default 0.6/0.4

5. **Fact Invalidation Strategy**
   - Question: Should we delete or mark outdated facts?
   - Recommendation: Mark with superseded_by (transparent), filter at retrieval
   - Resolution: Keep both, filter in RAG service (preserves history)

---

**Next Artifact**: specs.md

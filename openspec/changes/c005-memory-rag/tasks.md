# Tasks Artifact: c005-memory-rag

**Generated**: 2026-01-28
**Change**: c005-memory-rag
**Schema**: spec-factory v1

---

## 1. Implementation Checklist

### 1.1 Phase 1: Memory Services (Infrastructure Layer)

| Task | File | Lines (est.) | Status | Notes |
|------|------|--------------|--------|-------|
| Create QdrantVectorStoreAdapter | `infrastructure/database/qdrant_vector_store.py` | 100 | ⬜ | Tier 2 + Tier 3 storage, collection management |
| Create Mem0MemoryAdapter | `infrastructure/external/mem0_memory.py` | 80 | ⬜ | Advanced consolidation, DSPy integration |
| Create memory config | `core/memory_config.py` | 50 | ⬜ | Qdrant URL, collection names |

### 1.2 Phase 2: Domain and Application Layer

| Task | File | Lines (est.) | Status | Notes |
|------|------|--------------|--------|-------|
| Create MemoryConsolidationEntity | `domain/entities/memory_consolidation.py` | 80 | ⬜ | @dataclass, state transitions (LOCKED) |
| Create MemoryRepository interface | `domain/repositories/memory_repository.py` | 60 | ⬜ | ABC with 6 methods (LOCKED) |
| Create StoreMemoryUseCase | `application/use_cases/store_memory_use_case.py` | 80 | ⬜ | Temporal metadata enrichment |
| Create SearchMemoryUseCase | `application/use_cases/search_memory_use_case.py` | 100 | ⬜ | Multi-hop RAG, filtering |
| Create ConsolidateMemoryUseCase | `application/use_cases/consolidate_memory_use_case.py` | 120 | ⬜ | Tier 2 → Tier 3 migration |
| Create TemporalRAGService | `application/services/temporal_rag_service.py` | 150 | ⬜ | Time-aware search, classification |
| Create DurationMemoryService | `application/services/duration_memory_service.py` | 100 | ⬜ | State tracking, consolidation |
| Create memory DTOs | `application/dtos/memory_dtos.py` | 120 | ⬜ | All request/response schemas |

### 1.3 Phase 3: Presentation Layer

| Task | File | Lines (est.) | Status | Notes |
|------|------|--------------|--------|-------|
| Create memory routes | `presentation/api/v1/memory_routes.py` | 100 | ⬜ | 7 REST endpoints |
| Create health check | `presentation/api/v1/memory_health.py` | 40 | ⬜ | Service readiness (port 8022) |

### 1.4 Phase 5: Frontend Types

| Task | File | Lines (est.) | Status | Notes |
|------|------|--------------|--------|-------|
| Create memory types | `frontend/types/memory.ts` | 120 | ⬜ | Zod schemas matching Pydantic |
| Create memory hooks | `frontend/hooks/useMemory.ts` | 80 | ⬜ | Memory API calls |
| Create memory components | `frontend/components/MemoryPanel.tsx` | 100 | ⬜ | Memory visualization (future) |

### 1.5 Phase 6: Testing

| Task | Type | Status | Notes |
|------|------|--------|-------|
| Unit tests for TemporalRAGService | `tests/unit/test_temporal_rag.py` | ⬜ | Temporal filtering, fact invalidation |
| Unit tests for DurationMemoryService | `tests/unit/test_duration_memory.py` | ⬜ | State tracking, duration calculation |
| Unit tests for ConsolidateMemoryUseCase | `tests/unit/test_consolidation.py` | ⬜ | Tier 2 → Tier 3 migration |
| Integration tests | `tests/integration/test_memory_pipeline.py` | ⬜ | End-to-end memory flow |
| Consolidation tests | `tests/integration/test_consolidation.py` | ⬜ | Merge, invalidation, summarization |

---

## 2. Verification Steps

### 2.1 Code Quality

```bash
# Run all quality checks
cd /home/riju279/Documents/Code/XRIG/AgentX/agentx
ruff check . --fix
ruff format .
pyrefly check . --summarize-errors

# Frontend type check
cd /home/riju279/Documents/Code/XRIG/AgentX/frontend
npx tsc --noEmit
```

### 2.2 File Size Validation

```bash
# Verify no file exceeds 150 lines
find agentx/ -name "*.py" -exec wc -l {} + | awk '$1 > 150 {print "FILE TOO LARGE:", $2}'

# Memory services specifically
wc -l agentx/infrastructure/database/qdrant_vector_store.py
wc -l agentx/application/services/temporal_rag_service.py
wc -l agentx/application/use_cases/consolidate_memory_use_case.py
```

### 2.3 Import Validation

```bash
# Verify no relative imports (forbidden by CLAUDE_POLICY.md)
grep -r "from \.\." agentx/  # Should return nothing
grep -r "from \." agentx/ | grep -v "from \.\.\."  # Should return nothing

# Verify absolute imports only
grep -r "^from agentx" agentx/ | head -20  # Should show results
```

### 2.4 LLD Alignment Validation

```bash
# Verify MemoryConsolidationEntity matches LLD
grep -A 10 "class MemoryConsolidationEntity" agentx/domain/entities/memory_consolidation.py
# Should match: domain_model.md:189-269

# Verify MemoryRepository matches LLD
grep -A 5 "class MemoryRepository" agentx/domain/repositories/memory_repository.py
# Should match: domain_model.md:531-592
```

### 2.5 Qdrant Connection Validation

```bash
# Verify Qdrant is running
curl http://localhost:6333/

# Verify collections exist
curl http://localhost:6333/collections/agentx_user_default
```

### 2.6 Integration Tests

```bash
# Run integration tests
pytest tests/integration/test_memory_pipeline.py -v
pytest tests/integration/test_consolidation.py -v

# Run stress test (1000 memories)
pytest tests/integration/test_memory_consolidation_stress.py -v
```

---

## 3. Acceptance Criteria

### 3.1 Functional Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| **Temporal metadata added** | Unit test store_memory | created_at, valid_from, temporal_type present |
| **Temporal classification** | Unit test with samples | >90% accuracy |
| **Time-filtered search** | Integration test | Recent returns last 30 days only |
| **Fact invalidation** | Integration test with conflicts | Outdated facts marked or filtered |
| **Multi-hop retrieval** | Integration test | Tier 2 + Tier 3 results merged |
| **Consolidation reduces Tier 2** | Integration test | Tier 2 count decreases after consolidation |
| **Duplicate merging** | Integration test | merge_rate > 0.1 |
| **Duration tracking** | Unit test | start_state → end_state → duration calculated |
| **Duration consolidation** | Integration test | Duration memory stored to Tier 3 |
| **All three triggers work** | Integration test | SCHEDULED, MANUAL, PRE_QUERY all fire |

### 3.2 Non-Functional Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| **Consolidation latency** | Benchmark (10 sessions) | <30s |
| **Search latency** | Benchmark (100 queries) | P95 < 500ms |
| **Tier 3 search** | Benchmark | P95 < 300ms |
| **Multi-hop merge** | Benchmark | <100ms |
| **Merge rate** | Consolidation test | >10% |
| **Temporal classification** | Validation test | >90% accuracy |
| **Multi-hop improvement** | Comparison test | +15% over Tier 3 alone |
| **Code quality** | `ruff check`, `ruff format` | Zero errors |
| **Type checking** | `pyrefly check` | Zero errors |
| **File sizes** | `find + wc` | All files < 150 lines |
| **Import rules** | `grep "from \."` | Zero relative imports |
| **TypeScript compiles** | `npx tsc --noEmit` | Zero errors |

### 3.3 Integration Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| **C001 alignment** | File structure check | Clean Architecture layers match |
| **C002 alignment** | DTO usage | All DTOs follow Pydantic v2 patterns |
| **C003 integration** | RAGDSPyAgent extension | TemporalRAGService integrated |
| **Qdrant connection** | `curl http://localhost:6333/` | Returns Qdrant info |

---

## 4. Definition of Done

C005-memory-rag is **complete** when:

- [ ] All 3 memory services created (Qdrant, Mem0AI, config)
- [ ] MemoryConsolidationEntity created (100% LLD match)
- [ ] MemoryRepository interface implemented
- [ ] All use cases created (Store, Search, Consolidate)
- [ ] TemporalRAGService implemented (classification, filtering, invalidation)
- [ ] DurationMemoryService implemented (state tracking)
- [ ] REST endpoints created (7 endpoints on port 8021)
- [ ] Health check endpoint (port 8022)
- [ ] All DTOs created with Pydantic → Zod alignment
- [ ] Frontend Zod schemas match backend Pydantic
- [ ] Zero field name mismatches with LLD
- [ ] Zero relative imports (absolute only)
- [ ] All files under 150 lines
- [ ] All quality checks pass (ruff, pyrefly, tsc)
- [ ] Integration tests pass (memory pipeline, consolidation)
- [ ] Temporal classification >90% accuracy
- [ ] Fact invalidation works end-to-end
- [ ] Consolidation reduces Tier 2 memory count
- [ ] Merge rate >10%
- [ ] Multi-hop retrieval +15% better than Tier 3 alone

---

## 5. Rollback Plan

If implementation fails:

1. **Identify failure point**:
   ```bash
   # Check which test failed
   pytest tests/integration/test_memory_pipeline.py -v

   # Check service health
   curl http://localhost:8021/api/v1/memory/health
   ```

2. **Rollback steps**:
   ```bash
   # Remove created files
   rm -rf agentx/infrastructure/database/qdrant_vector_store.py
   rm -rf agentx/infrastructure/external/mem0_memory.py
   rm -rf agentx/domain/entities/memory_consolidation.py
   rm -rf agentx/domain/repositories/memory_repository.py
   rm -rf agentx/application/use_cases/store_memory_use_case.py
   rm -rf agentx/application/use_cases/search_memory_use_case.py
   rm -rf agentx/application/use_cases/consolidate_memory_use_case.py
   rm -rf agentx/application/services/temporal_rag_service.py
   rm -rf agentx/application/services/duration_memory_service.py
   rm -rf agentx/application/dtos/memory_dtos.py
   rm -rf agentx/presentation/api/v1/memory_routes.py
   rm -rf agentx/presentation/api/v1/memory_health.py
   rm -rf frontend/types/memory.ts
   ```

3. **Recovery actions**:
   - Re-run from Phase 1 (Memory Services)
   - Verify Qdrant connection before proceeding
   - Test Tier 2 storage before Tier 3
   - Add integration tests incrementally

---

## 6. Dependencies Unlocked

This change unlocks:

| Change | Unlocked Feature |
|--------|-----------------|
| **Future: Memory Analytics** | Can track memory patterns, temporal trends |
| **Future: Memory UI** | Can visualize memories, timeline view |
| **Future: Advanced RAG** | Can add multi-hop, recursive retrieval |

---

## 7. Verification Checklist

Before marking C005-memory-rag complete, verify:

- [x] All 7 artifacts created (scan, extract, validate, proposal, specs, design, tasks)
- [ ] All implementation tasks in Phase 1 complete
- [ ] All implementation tasks in Phase 2 complete
- [ ] All implementation tasks in Phase 3 complete
- [ ] All implementation tasks in Phase 4 complete
- [ ] Code quality checks pass
- [ ] LLD alignment verified (grep tests pass)
- [ ] Integration tests pass
- [ ] Temporal classification validated
- [ ] Fact invalidation validated
- [ ] Consolidation validated

---

**End of spec-factory pipeline**

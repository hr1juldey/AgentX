# Proposal: c006-release-plan

**Generated**: 2026-01-28
**Change**: c006-release-plan
**Schema**: spec-factory v1

---

## Summary

Define an 8-phase incremental delivery strategy that builds AgentX from minimal FastAPI server to production-hardened AI assistant. Each phase completes in 2-3 hours, freezes its APIs upon completion, and has explicit verification criteria. This approach enables manageable development steps, parallel team work, and continuous validation.

---

## Motivation

### Problem Statement

Building a full-featured AI assistant like AgentX is a massive undertaking. Traditional "big bang" delivery has critical flaws:

1. **No intermediate milestones** - No working system until everything is complete
2. **Late validation** - Integration issues discovered only at the end
3. **Blocked parallel development** - Teams wait for each other to complete APIs
4. **Unclear progress** - Hard to measure how close to "done"
5. **Risk accumulation** - All risk deferred to final integration

### Current State

- **C001-C005 Complete**: All foundational specifications defined
  - C001: Clean Architecture file structure
  - C002: Pydantic v2 → Zod alignment
  - C003: DSPy agents + LangGraph state machines
  - C004: Voice streaming (STT/TTS/VAD)
  - C005: Temporal RAG + memory consolidation

- **LLD Available**: `incremental_release_plan.md` defines 8-phase approach
  - Phase 0: Server Setup (2-3 hours)
  - Phase 1: Domain + Infrastructure (2-3 hours)
  - Phase 2: Main DSPy Agent (2-3 hours)
  - Phase 3: UI + Streaming (2-3 hours)
  - Phase 4: State Machines (2-3 hours)
  - Phase 5: Memory + RAG (2-3 hours)
  - Phase 6: Plugins (2-3 hours)
  - Phase 7: Production Hardening (2-3 hours)

- **Total Scope**: ~16-24 hours of implementation work (8 phases × 2-3 hours)

### Desired State

Structured release plan that:
- **Breaks work into 8 phases** - Each phase is 2-3 hours, clearly scoped
- **Freezes APIs after each phase** - No breaking changes to completed phases
- **Provides verification criteria** - Each phase has explicit tests
- **Enables parallel development** - Multiple teams can work on different phases simultaneously
- **Delivers usable increments** - Each phase produces a releasable system

---

## Scope

### In Scope

- **8-Phase Definition**: Detailed scope and deliverables for each phase
- **API Freezing Strategy**: Rules for freezing APIs, handling breaking changes
- **Verification Criteria**: Health checks, unit tests, integration tests for each phase
- **Dependency Graph**: Phase 0→1→2→3→4→5→6→7 ordering and dependencies
- **Integration with C001-C005**: Mapping of changes to phases they enable

### Out of Scope

- **Individual Phase Implementation** - Covered by C001-C005 specifications
  - Phase 0 implementation details (server setup) - straightforward
  - Phase 1 implementation details (entities, repositories) - covered by C001
  - Phase 2-7 implementation details - covered by C003, C004, C005
- **Post-Release Maintenance** - Monitoring, updates, feature additions (future concern)
- **Deployment Automation** - CI/CD, Docker, infrastructure (future concern)

### Dependencies

| Change | Status | Required For |
|--------|--------|--------------|
| **C001-folder-structure** | Complete | All phases (Clean Architecture layers) |
| **C002-data-contracts** | Complete | Phase 2+ (Pydantic DTOs for API) |
| **C003-agent-pipeline** | Complete | Phase 2-4 (DSPy agents, LangGraph) |
| **C004-voice-streaming** | Complete | Phase 7 (voice integration) |
| **C005-memory-rag** | Complete | Phase 5 (memory services) |

---

## Success Criteria

1. **All 8 Phases Defined**
   - Measure: Count phases with scope and deliverables
   - Target: 8 phases (0, 1, 2, 3, 4, 5, 6, 7)

2. **API Freezing Rules Documented**
   - Measure: Count API freezing rules defined
   - Target: ≥3 rules (freeze, breaking changes, versioning)

3. **Verification Criteria Complete**
   - Measure: Count phases with verification criteria
   - Target: 8/8 phases have explicit tests

4. **Dependency Graph Established**
   - Measure: Phase dependency relationships documented
   - Target: Linear chain (0→1→2→3→4→5→6→7) with Phase 7 depending on all

5. **Change-to-Phase Mapping Complete**
   - Measure: Count changes mapped to phases
   - Target: C001-C005 all mapped to phases they enable

6. **LLD Alignment Verified**
   - Measure: Field name match with incremental_release_plan.md
   - Target: 100% match (no drift)

---

## Implementation Approach

### High-Level Approach

1. **Define 8-Phase Strategy** (this change)
   - Document each phase's scope, deliverables, frozen APIs
   - Establish API freezing rules
   - Create verification criteria for each phase

2. **Map C001-C005 to Phases** (this change)
   - C001 enables all phases (Clean Architecture foundation)
   - C002 enables Phase 2+ (DTOs required for API)
   - C003 enables Phase 2-4 (DSPy agents, LangGraph)
   - C004 enables Phase 7 (voice services)
   - C005 enables Phase 5 (memory services)

3. **Create Dependency Graph** (this change)
   - Establish linear ordering: 0→1→2→3→4→5→6→7
   - Identify which phases depend on which
   - Enable parallel development planning

4. **Document Verification Strategy** (this change)
   - Health check endpoints for all components
   - Unit test framework configuration
   - Integration test scenarios
   - Coverage targets (70% in Phase 7)

### Key Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| **8 phases of 2-3 hours** | Manageable chunks, fits in half-day sprints | 4 phases (too large), 16 phases (too granular) |
| **API freezing after each phase** | Enables parallel development, prevents breaking changes | No freezing (chaos), Semantic versioning (more complex) |
| **Linear dependency chain** | Simple ordering, clear progression | Circular dependencies (impossible), Parallel starts (blocked) |
| **Verification per phase** | Continuous validation, early issue detection | Big bang testing (late discovery) |
| **LLD as source of truth** | Locked definitions prevent drift | Working specs (diverge from LLD) |

### Constraints

- **Phase Duration**: Must be 2-3 hours each (enforced by scope limits)
- **API Freezing**: No breaking changes to completed phases
- **LLD Alignment**: 100% match with incremental_release_plan.md
- **Verification**: Every phase must pass health check + tests
- **Dependencies**: All C001-C005 must be complete before Phase 0

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Phase takes >3 hours** | Medium | Medium | Strict scope limits, stub unimplemented items with NotImplementedError |
| **API breaking change needed** | Low | High | Create new major version instead of modifying frozen API |
| **Dependency not ready** | Low | High | Verify C001-C005 complete before starting Phase 0 |
| **Verification criteria unclear** | Low | Medium | Each phase has explicit health check and test requirements |
| **Phase scope creep** | Medium | Medium | Document scope boundaries, defer to later phases |
| **Integration issues between phases** | Medium | High | Phase 7 dedicated to hardening and integration testing |

---

## Open Questions

1. **Phase Duration Flexibility**
   - Question: Can phases take longer than 3 hours if needed?
   - Recommendation: Strict 2-3 hour target, split if longer
   - Resolution: Enforce 3-hour limit, create sub-phases if needed

2. **API Versioning Strategy**
   - Question: How to handle API versions across phases?
   - Recommendation: No versioning within phase, new major version for breaking changes
   - Resolution: Document in api-freezing spec

3. **Parallel Development**
   - Question: Can multiple teams work on different phases simultaneously?
   - Recommendation: Yes, after API freezing
   - Resolution: Document in incremental-delivery spec

4. **Phase Completion Definition**
   - Question: What defines "complete" for a phase?
   - Recommendation: All implemented items done, stubbed items raise NotImplementedError, verification passes
   - Resolution: Document in verification-criteria spec

5. **Rollback Strategy**
   - Question: What if a phase needs to be redone?
   - Recommendation: Incremental git commits per phase, easy rollback
   - Resolution: Document in tasks.md

---

## Phase Overview

| Phase | Duration | Focus | Deliverables | APIs Frozen |
|-------|----------|-------|--------------|-------------|
| **Phase 0** | 2-3 hours | Server Setup | FastAPI, Config, DI | Settings structure |
| **Phase 1** | 2-3 hours | Domain + Infrastructure | Entities, Repositories, Adapters | Entity structures, Repository interfaces |
| **Phase 2** | 2-3 hours | Main Agent | DSPy ReAct, Tools | Agent signature |
| **Phase 3** | 2-3 hours | UI + Streaming | UI Agent, Descriptors, WebSocket | Descriptor schemas |
| **Phase 4** | 2-3 hours | State Machines | LangGraph nodes, transitions | State schemas |
| **Phase 5** | 2-3 hours | Memory + RAG | Mem0AI, RAG Agent, Consolidation | RAG interface |
| **Phase 6** | 2-3 hours | Plugins | Plugin interface, Permissions | Plugin protocol |
| **Phase 7** | 2-3 hours | Hardening | Tests, Error handling, Monitoring | Complete system |

**Total Estimated Time**: 16-24 hours

---

**Next Artifact**: specs.md

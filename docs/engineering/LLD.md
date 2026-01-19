# AGENTX Low-Level Design (LLD)

**Version**: 1.0.0
**Date**: 2026-01-19
**Status**: Locked
**Part of**: AGENTX Engineering Documentation

---

## Executive Summary

This Low-Level Design (LLD) provides complete implementation specifications for AGENTX Generative UI. All class names, function names, inputs/outputs, and data types are **locked and immutable**.

**Non-Compliance Clause**: Any implementation that deviates from these specifications is invalid and must be corrected.

---

## Document Map

| Document | Purpose | Scope | Dependencies |
|----------|---------|-------|--------------|
| **[LLD.md](LLD.md)** | Master index, navigation, glossary | All documents | None |
| **[lld/domain_model.md](lld/domain_model.md)** | Entities, Value Objects, Aggregates, Repositories | Domain layer | None |
| **[lld/application_services.md](lld/application_services.md)** | Use cases, Commands, Queries, DTOs, Mappers | Application layer | domain_model.md |
| **[lld/infrastructure_adapters.md](lld/infrastructure_adapters.md)** | DB, cache, queue, external service adapters | Infrastructure layer | domain_model.md |
| **[lld/agent_runtime.md](lld/agent_runtime.md)** | DSPy agents, LangGraph nodes, tools | Agent layer | domain_model.md, infrastructure_adapters.md |
| **[lld/ui_descriptor_contract.md](lld/ui_descriptor_contract.md)** | UI descriptors, schemas, lifecycle | UI contract | domain_model.md |
| **[lld/plugin_system.md](lld/plugin_system.md)** | Plugin boundaries, registration, lifecycle | Plugin layer | domain_model.md |
| **[lld/incremental_release_plan.md](lld/incremental_release_plan.md)** | 2-3 hour implementation slices | Release plan | All documents |

---

## Quick Navigation

### For Backend Developers

Start with:
1. [lld/domain_model.md](lld/domain_model.md) - Understand entities and repositories
2. [lld/application_services.md](lld/application_services.md) - Understand use cases and DTOs
3. [lld/infrastructure_adapters.md](lld/infrastructure_adapters.md) - Understand external integrations

Then proceed to:
4. [lld/agent_runtime.md](lld/agent_runtime.md) - Implement DSPy agents and tools
5. [lld/ui_descriptor_contract.md](lld/ui_descriptor_contract.md) - Understand UI streaming protocol

### For Frontend Developers

Start with:
1. [lld/ui_descriptor_contract.md](lld/ui_descriptor_contract.md) - Understand all 7 UI descriptors
2. WebSocket message types and flows
3. Lifecycle rules for each widget type

### For Plugin Developers

Start with:
1. [lld/plugin_system.md](lld/plugin_system.md) - Understand plugin interface and permissions
2. [Plugin interface](lld/plugin_system.md#1-plugin-interface) - Implement required methods
3. [Plugin permissions](lld/plugin_system.md#2-plugin-permissions) - Request appropriate permissions

---

## Architecture Overview

### Clean Architecture Layers

```
┌──────────────────────────────────────────────────────────────┐
│                    Presentation Layer                         │
│  (FastAPI Routes, WebSocket Handlers, Controllers)           │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    Application Layer                          │
│  (Use Cases, Commands, Queries, DTOs, Mappers)               │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                      Domain Layer                             │
│  (Entities, Value Objects, Aggregates, Domain Services)      │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                        │
│  (Qdrant, Redis, SQLite, Ollama, Mem0AI, WebSocket)          │
└──────────────────────────────────────────────────────────────┘
```

### Conference Room Agent Pattern

```
┌─────────────────────────────────────────────────────────────┐
│              CEO Agent (MainDSPyReActAgent)                 │
│         Coordinates specialists, makes decisions             │
└─────────────────────────────────────────────────────────────┘
                    │           │
        ┌───────────┘           └───────────┐
        ▼                                   ▼
┌───────────────────┐         ┌───────────────────────┐
│  UI Agent         │         │  RAG Agent            │
│  (UIDSPyAgent)    │         │  (RAGDSPyAgent)       │
│                   │         │                       │
│  - SelectWidget   │         │  - Retrieval          │
│  - ConfigureForm  │         │  - ContextInjection   │
│  - ShowCard       │         │  - Consolidation      │
│  - RequestConf    │         │                       │
└───────────────────┘         └───────────────────────┘
```

### Three-Tier Memory Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Tier 1: Short-Term (DSPy History)                          │
│  - Scope: Current conversation context                      │
│  - Retention: Sliding window (~10-20 turns)                 │
│  - Overflow: → Tier 2                                       │
└─────────────────────────────────────────────────────────────┘
                            │ (overflow)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Tier 2: Mid-Term (Agent's Qdrant Collection)               │
│  - Scope: Per-agent, per-session                            │
│  - Retention: TTL 30-90 days                                │
│  - Consolidation: → Tier 3                                  │
└─────────────────────────────────────────────────────────────┘
                            │ (consolidation)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Tier 3: Long-Term (User's Qdrant + Mem0AI)                 │
│  - Scope: Cross-session, persistent                         │
│  - Retention: User-controlled (90d/365d/forever)            │
│  - Trigger: Every 10 interactions + manual                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Design Decisions

### ADR-001: Multi-Signature Multi-Module ReAct Pattern

**Decision**: Use hierarchical multiple choice QnA with decision tree

**Rationale**: Better reasoning with small LLMs (gemma3:4b)

**Implementation**:
```python
class MainDSPyReActAgent(dspy.Module):
    def __init__(self, tools, max_iters=8):
        self.tool_selector = dspy.Predict(ToolSelectionSignature)
        self.confidence_scorer = dspy.Predict(ConfidenceScoringSignature)
        self.react = dspy.ReAct(MainAgentSignature, tools=tools)
```

### ADR-002: Dual LangGraph State Machines

**Decision**: Two state machines with conference pattern

**Rationale**: Clear separation of frontend and backend concerns

**Implementation**:
- `BackendLangGraphState`: Agent reasoning state
- `FrontendLangGraphState`: UI component state

### ADR-003: Hybrid Redis+SQLite Storage

**Decision**: Redis for active sessions (fast), SQLite for long-term (persistent)

**Rationale**: Fast access for active sessions, persistent storage for history

**Implementation**:
- `RedisSessionAdapter`: TTL 1 hour, < 10ms access
- `SQLiteSessionAdapter`: Permanent storage, < 100ms access

### ADR-004: Agentic RAG Architecture

**Decision**: RAG agent prepares context, injects if high confidence

**Rationale**: Avoids hallucination from poor context, higher quality

**Implementation**:
```python
class RAGDSPyAgent(dspy.Module):
    def should_inject_context(self, query, retrieved_context):
        decision = self.injection_decider(query, retrieved_context)
        return decision.should_inject  # Only if confidence > 0.7
```

### ADR-005: Plugin Opt-In Permissions

**Decision**: All permissions default to false, user must explicitly grant

**Rationale**: Security by default, user control

**Implementation**:
```python
class PluginPermissions(BaseModel):
    allow_ui_descriptors: bool = False
    allow_memory_access: bool = False
    allow_network_access: bool = False
```

---

## Incremental Release Plan

### Phase Overview

| Phase | Duration | Focus | APIs Frozen |
|-------|----------|-------|-------------|
| 0 | 2-3 hours | Server Setup | Settings |
| 1 | 2-3 hours | Domain + Infrastructure | Entities |
| 2 | 2-3 hours | Main Agent | Agent signatures |
| 3 | 2-3 hours | UI + Streaming | Descriptors |
| 4 | 2-3 hours | State Machines | State schemas |
| 5 | 2-3 hours | Memory + RAG | RAG interface |
| 6 | 2-3 hours | Plugins | Plugin protocol |
| 7 | 2-3 hours | Hardening | Complete system |

**Total Time**: 16-24 hours
**Total Code**: ~8600 lines, 100 files, 3500 tests

See [lld/incremental_release_plan.md](lld/incremental_release_plan.md) for detailed phase breakdown.

---

## Naming Conventions

### Function Prefixes

| Prefix | Purpose | Example |
|--------|---------|---------|
| `get_` | Retrieve single item | `get_by_id` |
| `list_` | Retrieve multiple items | `list_active_sessions` |
| `create_` | Create new entity | `create_session` |
| `update_` | Modify existing | `update_session` |
| `delete_` | Remove entity | `delete_session` |
| `is_` | Boolean check | `is_active` |
| `has_` | Boolean check | `has_permission` |
| `should_` | Boolean check | `should_consolidate` |

### Class Suffixes

| Suffix | Purpose | Example |
|--------|---------|---------|
| `Entity` | Domain entity | `AgentSessionEntity` |
| `DTO` | Data Transfer Object | `SessionResponseDTO` |
| `Repository` | Data access interface | `AgentSessionRepository` |
| `Adapter` | Infrastructure implementation | `QdrantVectorStoreAdapter` |
| `Service` | Business logic | `MemoryService` |
| `UseCase` | Application use case | `ExecuteAgentQueryUseCase` |
| `Signature` | DSPy signature | `MainAgentSignature` |
| `Descriptor` | UI component schema | `CardDescriptor` |

---

## Verification Checklist

Before implementation begins, verify:

- [ ] All 8 LLD documents are created and locked
- [ ] All class names follow naming conventions
- [ ] All function signatures are specified
- [ ] All data types are locked (Pydantic, TypedDict, Enum)
- [ ] All dependencies are documented (DAG verified)
- [ ] All APIs are frozen (no provisional names)
- [ ] Incremental release plan is validated (2-3 hours per phase)
- [ ] Testing strategy is aligned with locked structures
- [ ] No circular dependencies exist
- [ ] File structure follows Clean Architecture

---

## File Structure Reference

```
agentx/
├── core/                              # Configuration & DI
├── domain/                            # Business logic
│   ├── entities/                      # Core entities
│   ├── repositories/                  # Repository interfaces
│   └── services/                      # Domain services
├── application/                       # Use cases & orchestration
│   ├── use_cases/                     # Single-purpose classes
│   ├── commands/                      # Input DTOs
│   ├── queries/                       # Query DTOs
│   ├── dtos/                          # Output DTOs
│   └── mappers/                       # Entity ↔ DTO
├── infrastructure/                    # External concerns
│   ├── database/                      # DB adapters
│   └── external/                      # External service adapters
├── agent/                             # DSPy + LangGraph agents
│   ├── dspy_signatures/               # DSPy signatures
│   ├── tools/                         # DSPy tools
│   ├── dspy_agents/                   # DSPy agents
│   └── langgraph/                     # LangGraph state machines
├── ui/                                # UI descriptors
│   ├── descriptors/                   # Pydantic models
│   └── protocols/                     # WebSocket messages
├── plugin/                            # Plugin system
│   ├── interface.py                   # AgentXPlugin ABC
│   ├── permissions.py                 # PluginPermissions
│   ├── manifest.py                    # PluginManifest
│   └── registry.py                    # PluginRegistry
├── presentation/                      # FastAPI routes
│   └── api/v1/                        # REST endpoints
├── tests/                             # Test suite
│   ├── unit/                          # 70% of tests
│   ├── integration/                   # 20% of tests
│   └── e2e/                           # 10% of tests
└── main.py                            # Application entry point
```

---

## Testing Philosophy

### What CAN Be Mocked (Unit Tests)

- Domain entities (state transitions, business logic)
- Repository interfaces (in-memory implementations)
- DTOs and Mappers (data transformations)
- Configuration and dependency injection
- Pure functions (validators, formatters)

### What CANNOT Be Mocked (Integration Tests)

- **LLM calls** - Use real DSPy + real Ollama
- **Embeddings** - Use real embeddings
- **DSPy agents/signatures** - Use real DSPy with real LLM
- **RAG retrieval logic** - Use real Qdrant + real embeddings
- **Tool execution** - Use real tools

### Coverage Targets

| Layer | Target | Rationale |
|-------|--------|-----------|
| Domain | 90% | Critical business logic, fast tests |
| Application | 80% | Orchestration logic |
| Infrastructure | 70% | External dependencies |
| Agent | 60% | LLM behavior hard to test |
| **Overall** | **70%** | Balanced for AI system |

---

## Glossary

| Term | Definition |
|------|------------|
| **AgentSession** | User's conversation session with state tracking |
| **DSPy** | Programmatic LLM framework for agent development |
| **ReAct** | Reasoning and Acting pattern for agent loops |
| **LangGraph** | State machine framework for UI lifecycle |
| **UIDescriptor** | Pydantic model describing UI components |
| **Mem0AI** | Long-term memory system with consolidation |
| **Qdrant** | Vector database for semantic search |
| **Ollama** | Local LLM inference engine |
| **SHA256Hash** | Hashed user identifier for privacy |
| **TTL** | Time-To-Live for data expiration |
| **RAG** | Retrieval-Augmented Generation |
| **WebSocket** | Bidirectional real-time communication |
| **FastMCP** | Model Context Protocol server framework |
| **Clean Architecture** | Layered architecture pattern |
| **DDD** | Domain-Driven Design methodology |
| **DTO** | Data Transfer Object |

---

## Related Documentation

- **[HLD.md](HLD.md)** - High-Level Design (architecture overview)
- **[schemas.md](schemas.md)** - Data structure standards
- **[threat_model.md](threat_model.md)** - Security threat analysis
- **[privacy_assessment.md](privacy_assessment.md)** - PII handling and GDPR/CCPA compliance
- **[generative_ui_design_plan.md](generative_ui_design_plan.md)** - UI architecture plan

---

**This LLD is part of AGENTX v1.0. See [HLD.md](HLD.md) for high-level architecture.**

**Non-Compliance = Invalid Implementation. All names, types, and structures are immutable.**

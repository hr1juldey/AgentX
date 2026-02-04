# Spec: Folder Structure Conventions

## ADDED Requirements

### Requirement: Five-layer Clean Architecture
The system SHALL organize code into five architectural layers: `core/`, `domain/`, `application/`, `infrastructure/`, and `presentation/`.

#### Scenario: Layer dependency direction
- **WHEN** code in one layer imports from another layer
- **THEN** dependencies SHALL point inward only (presentation → application → domain ← infrastructure)

#### Scenario: Core layer contents
- **WHEN** developer places code in `core/`
- **THEN** it SHALL contain only global configuration, singleton dependencies, middleware, and exceptions

#### Scenario: Domain layer purity
- **WHEN** code is placed in `domain/`
- **THEN** it SHALL have zero external dependencies (no DSPy, no FastAPI, no external clients)

---

### Requirement: DSPy Signatures Placement
DSPy signatures SHALL be placed in `domain/signatures/` for reusable input/output contracts.

#### Scenario: Creating a new signature
- **WHEN** developer creates a reusable DSPy signature
- **THEN** signature SHALL be placed in `domain/signatures/<purpose>_signature.py`

#### Scenario: Signature naming
- **WHEN** signature file is created
- **THEN** file name SHALL be `{purpose}_signature.py` or group related signatures in one file

---

### Requirement: DSPy Agents Placement
DSPy agent implementations SHALL be placed in `application/agents/` with stem cell base class and differentiated subclasses.

#### Scenario: Stem cell agent location
- **WHEN** developer creates the base StemCellAgent
- **THEN** it SHALL be placed at `application/agents/stem_cell.py`

#### Scenario: Differentiated agent location
- **WHEN** developer creates a specialized agent (e.g., Researcher, Analyst)
- **THEN** it SHALL be placed at `application/agents/<agent_type>.py` extending StemCellAgent

---

### Requirement: DSPy Tools Placement
DSPy tools SHALL be placed in `application/tools/<domain>/` grouped by functional domain.

#### Scenario: Creating a web search tool
- **WHEN** developer creates a SearXNG search tool
- **THEN** tool SHALL be placed at `application/tools/web/search.py`

#### Scenario: Tool wrapper export
- **WHEN** tool function is implemented
- **THEN** it SHALL be wrapped with `dspy.Tool()` and exported as `{tool_name}_tool`

---

### Requirement: LangGraph Components Placement
LangGraph-related code SHALL be placed in `application/graphs/` with subdirectories for builder, routing, mutation, storage, and presets.

#### Scenario: Graph compiler placement
- **WHEN** developer creates DSPy → LangGraph compilation logic
- **THEN** it SHALL be placed in `application/graphs/builder/graph_compiler.py`

#### Scenario: Routing logic placement
- **WHEN** developer creates dynamic routing between graphs
- **THEN** it SHALL be placed in `application/graphs/routing/router.py`

#### Scenario: Mutation operations placement
- **WHEN** developer creates graph mutation (add_node, remove_edge, etc.)
- **THEN** it SHALL be placed in `application/graphs/mutation/<operation>.py`

#### Scenario: Graph storage placement
- **WHEN** developer creates graph persistence to Qdrant
- **THEN** it SHALL be placed in `application/graphs/storage/graph_store.py`

#### Scenario: Preset graph placement
- **WHEN** developer creates a predefined graph template
- **THEN** it SHALL be placed in `application/graphs/presets/<graph_type>_graph.py`

---

### Requirement: Pydantic Models Separation
Pydantic models SHALL be separated into `application/models/` for internal DSPy models and `presentation/models/` for API DTOs.

#### Scenario: Internal DSPy model placement
- **WHEN** developer creates a Pydantic model for DSPy internal use
- **THEN** it SHALL be placed in `application/models/<model_name>.py`

#### Scenario: API DTO placement
- **WHEN** developer creates a Pydantic model for API request/response
- **THEN** it SHALL be placed in `presentation/models/requests.py` or `presentation/models/responses.py`

---

### Requirement: Infrastructure Clients Placement
External service clients SHALL be placed in `infrastructure/<category>/` by service type.

#### Scenario: Memory system client placement
- **WHEN** developer creates Mem0AI or Qdrant client
- **THEN** it SHALL be placed in `infrastructure/memory/<service>_client.py`

#### Scenario: Voice client placement (using existing SDK)
- **WHEN** developer integrates Kyutai voice service
- **THEN** adapter SHALL be placed in `infrastructure/voice/voice_adapter.py` wrapping `libs/voice_client/` SDK

#### Scenario: Voice gateway placement
- **WHEN** developer creates WebSocket gateway for voice
- **THEN** it SHALL be placed in `infrastructure/voice/voice_gateway.py`

#### Scenario: Retrieval client placement
- **WHEN** developer creates RAG or search client
- **THEN** it SHALL be placed in `infrastructure/retrieval/<client_name>.py`

---

### Requirement: API Routes Organization
FastAPI routes SHALL be organized in `presentation/api/v1/<domain>/routes.py` with one routes file per domain.

#### Scenario: Agent endpoint placement
- **WHEN** developer creates agent-related endpoints
- **THEN** routes SHALL be placed in `presentation/api/v1/agents/routes.py`

#### Scenario: Graph endpoint placement
- **WHEN** developer creates graph management endpoints
- **THEN** routes SHALL be placed in `presentation/api/v1/graphs/routes.py`

#### Scenario: Single routes file per domain
- **WHEN** multiple endpoints exist for the same domain
- **THEN** all endpoints SHALL be in one `routes.py` file for that domain

---

### Requirement: Central Configuration
All environment variables SHALL be defined in `core/config.py` using Pydantic Settings.

#### Scenario: Adding new environment variable
- **WHEN** developer adds a new configurable value
- **THEN** it SHALL be added as a field to the Settings class in `core/config.py`

#### Scenario: Settings singleton
- **WHEN** application needs configuration values
- **THEN** it SHALL access the singleton `settings` instance from `core/config.py`

---

### Requirement: Absolute Imports Only
All imports SHALL use absolute paths starting with `from agentx.` - relative imports (`from .` or `from ..`) are prohibited.

#### Scenario: Importing from domain layer
- **WHEN** code imports a domain entity
- **THEN** import SHALL be `from agentx.domain.entities.graph import Graph`

#### Scenario: Importing application code
- **WHEN** code imports an agent
- **THEN** import SHALL be `from agentx.application.agents.stem_cell import StemCellAgent`

#### Scenario: Relative import rejection
- **WHEN** code uses `from .graph import Graph` or `from ..agents import StemCellAgent`
- **THEN** ruff SHALL flag as error and developer SHALL fix to absolute import

---

### Requirement: File Size Limits
Source files SHALL NOT exceed 100 lines of executable code (plus 50 lines of overhead for imports and comments).

#### Scenario: File exceeds limit
- **WHEN** file exceeds 100 lines of executable code
- **THEN** developer SHALL split file into submodules

#### Scenario: Submodule creation
- **WHEN** file is split due to size limit
- **THEN** related functions SHALL be grouped in subdirectory (e.g., `builder/`, `routing/`)

---

### Requirement: Lifespan Management
Application startup and shutdown hooks SHALL be defined in `main.py` using FastAPI lifespan context manager.

#### Scenario: DSPy initialization on startup
- **WHEN** application starts
- **THEN** `ensure_dspy_configured()` SHALL be called to configure global LM/RM

#### Scenario: Client initialization on startup
- **WHEN** application starts
- **THEN** external clients (Mem0AI, Qdrant, voice) SHALL be initialized via dependency getters

#### Scenario: Cleanup on shutdown
- **WHEN** application shuts down
- **THEN** connections SHALL be closed and resources released

---

### Requirement: Graph Entities Placement
Core business entities for graph lifecycle SHALL be placed in `domain/entities/` as dataclasses.

#### Scenario: Graph entity placement
- **WHEN** developer creates entity for graph specification
- **THEN** it SHALL be placed at `domain/entities/graph.py` as `@dataclass`

#### Scenario: Mutation entity placement
- **WHEN** developer creates entity for graph mutation operations
- **THEN** it SHALL be placed at `domain/entities/mutation.py` as `@dataclass`

#### Scenario: Execution entity placement
- **WHEN** developer creates entity for graph execution tracking
- **THEN** it SHALL be placed at `domain/entities/execution.py` as `@dataclass`

---

### Requirement: Evaluation and Coordination Placement
Critic, evaluator, and coordinator logic SHALL be placed in `application/evaluation/` and `application/coordination/`.

#### Scenario: Critic placement
- **WHEN** developer creates graph execution quality evaluator
- **THEN** it SHALL be placed at `application/evaluation/critic.py`

#### Scenario: Coordinator placement
- **WHEN** developer creates continue/replan/mutate decision logic
- **THEN** it SHALL be placed at `application/coordination/coordinator.py`

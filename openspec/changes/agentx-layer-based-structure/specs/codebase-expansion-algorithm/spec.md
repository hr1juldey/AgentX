# Spec: Codebase Expansion Algorithm

## ADDED Requirements

### Requirement: New Agent Type Addition Algorithm
When adding a new agent type, developers SHALL follow a defined sequence of steps across multiple directories.

#### Scenario: Creating signature
- **WHEN** developer needs a new agent type
- **THEN** developer SHALL first create signature in `domain/signatures/<agent>_signature.py` if new pattern is needed

#### Scenario: Creating agent class
- **WHEN** signature is defined or reused
- **THEN** developer SHALL create agent in `application/agents/<agent>.py` extending StemCellAgent

#### Scenario: Adding tools
- **WHEN** agent needs external capabilities
- **THEN** developer SHALL add tools in `application/tools/<domain>/`

#### Scenario: Creating use case
- **WHEN** agent requires orchestration logic
- **THEN** developer SHALL create use case in `application/use_cases/<operation>.py`

#### Scenario: Adding API routes
- **WHEN** agent needs API exposure
- **THEN** developer SHALL add routes in `presentation/api/v1/agents/routes.py`

#### Scenario: Adding DTOs
- **WHEN** API routes are added
- **THEN** developer SHALL add DTOs in `presentation/models/{requests,responses}.py`

---

### Requirement: New Tool Addition Algorithm
When adding a new tool for agent use, developers SHALL implement function, wrap with DSPy Tool, and register in agent.

#### Scenario: Implementing tool function
- **WHEN** developer creates a new tool
- **THEN** function SHALL be implemented in `application/tools/<domain>/<tool>.py`

#### Scenario: Wrapping with DSPy Tool
- **WHEN** tool function is implemented
- **THEN** function SHALL be wrapped with `dspy.Tool()` and exported as `{tool_name}_tool`

#### Scenario: Registering tool in agent
- **WHEN** tool needs to be available to agent
- **THEN** tool SHALL be registered in agent's `__init__` via `self.add_tool()`

---

### Requirement: External Service Integration Algorithm
When adding external service integration, developers SHALL create client, add configuration, handle lifespan, and create wrapper.

#### Scenario: Creating client
- **WHEN** integrating external service
- **THEN** client SHALL be created in `infrastructure/<category>/<service>_client.py`

#### Scenario: Adding configuration
- **WHEN** client requires configuration
- **THEN** config entries SHALL be added to `core/config.py` (URLs, API keys)

#### Scenario: Adding lifespan initialization
- **WHEN** client requires connection pooling
- **THEN** initialization SHALL be added to `main.py` lifespan hook

#### Scenario: Creating wrapper
- **WHEN** agents need to use the service
- **THEN** wrapper SHALL be created in `application/tools/` using DSPy Tool pattern

---

### Requirement: Domain-First Expansion Sequence
Codebase expansion SHALL start with domain entities and signatures before moving to application, infrastructure, and presentation layers.

#### Scenario: Creating domain entity first
- **WHEN** adding new feature requiring business entity
- **THEN** entity SHALL be created first in `domain/entities/` as `@dataclass`

#### Scenario: Creating or reusing signature
- **WHEN** domain entity exists
- **THEN** signature SHALL be created in `domain/signatures/` or reused if existing pattern matches

#### Scenario: Implementing application layer
- **WHEN** domain layer is stable
- **THEN** agent SHALL be implemented in `application/agents/` depending on domain entities and signatures

#### Scenario: Adding infrastructure
- **WHEN** application layer needs external services
- **THEN** infrastructure clients SHALL be added in `infrastructure/` implementing domain interfaces

#### Scenario: Adding presentation layer
- **WHEN** application layer is complete
- **THEN** API routes SHALL be added in `presentation/api/v1/` exposing application functionality

---

### Requirement: Import Path Update After Folder Creation
When new folders are created or code is moved, developers SHALL immediately update all import paths to use absolute imports.

#### Scenario: Updating imports after move
- **WHEN** code is moved to new folder structure
- **THEN** all importing files SHALL be updated to use new absolute import paths

#### Scenario: Running ruff to fix imports
- **WHEN** imports are updated
- **THEN** developer SHALL run `ruff check --fix` to auto-fix import issues

#### Scenario: Verifying no broken imports
- **WHEN** imports are updated
- **THEN** developer SHALL run tests to verify no broken imports remain

---

### Requirement: File Splitting When Size Limit Exceeded
When a file exceeds the 100-line executable code limit, developers SHALL split it into submodules.

#### Scenario: Detecting size limit exceeded
- **WHEN** file exceeds 100 lines of executable code
- **THEN** developer SHALL split file into logical submodules

#### Scenario: Creating subdirectory
- **WHEN** related functions are grouped for splitting
- **THEN** subdirectory SHALL be created (e.g., `builder/`, `routing/`)

#### Scenario: Moving functions to submodule
- **WHEN** file is split
- **THEN** related functions SHALL be moved to submodule files

#### Scenario: Updating imports after split
- **WHEN** file is split into submodules
- **THEN** imports SHALL be updated to reference new submodule locations

---

### Requirement: Quality Checks After Each Expansion Step
After each expansion step (agent, tool, service), developers SHALL run code quality tools to ensure compliance.

#### Scenario: Running ruff check
- **WHEN** code is added or modified
- **THEN** developer SHALL run `ruff check --fix` to catch and fix issues

#### Scenario: Running ruff format
- **WHEN** code passes ruff check
- **THEN** developer SHALL run `ruff format` to ensure consistent formatting

#### Scenario: Running pyrefly check
- **WHEN** code is formatted
- **THEN** developer SHALL run `pyrefly check --summarize-errors` to verify type correctness

#### Scenario: Fixing errors before proceeding
- **WHEN** quality tools report errors
- **THEN** developer SHALL fix all errors before proceeding to next expansion step

---

### Requirement: API Contract Stability When Adding Features
When adding features that affect API, developers SHALL maintain backward compatibility by adding new endpoints rather than modifying existing ones.

#### Scenario: Adding new API endpoint
- **WHEN** new feature requires API exposure
- **THEN** new endpoint SHALL be added without modifying existing endpoints

#### Scenario: Deprecating old endpoint
- **WHEN** endpoint must be replaced
- **THEN** old endpoint SHALL be marked deprecated but remain functional for one major version

#### Scenario: API documentation update
- **WHEN** API endpoints are added or modified
- **THEN** OpenAPI specification SHALL be updated to reflect changes

---

### Requirement: Test Creation Alongside Implementation
When expanding codebase with new features, developers SHALL create tests alongside implementation code.

#### Scenario: Test file placement
- **WHEN** new code is added
- **THEN** test file SHALL be created at `tests/unit/<path_matching_source>/test_<module>.py`

#### Scenario: Test coverage for agents
- **WHEN** agent is implemented
- **THEN** tests SHALL cover signature validation, tool registration, and forward method

#### Scenario: Test coverage for tools
- **WHEN** tool is implemented
- **THEN** tests SHALL cover function execution and DSPy Tool wrapper

#### Scenario: Test coverage for infrastructure
- **WHEN** infrastructure client is implemented
- **THEN** tests SHALL use mocks to avoid external dependencies

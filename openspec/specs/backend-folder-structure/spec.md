# Spec: backend-folder-structure

**File**: `specs/backend-folder-structure/spec.md`

## 1.1 Purpose

Define the backend folder structure for Real AgentX v0.1, following Clean Architecture principles from mimicus with locked entities from LLD.

## 1.2 Scope

**In Scope**:
- 7-layer Clean Architecture: core/, domain/, infrastructure/, agent/, ui/, application/, presentation/
- File placement rules for each layer
- Import patterns (absolute only)
- File size limits (150 lines max)

**Out of Scope**:
- Runtime behavior (see C003-agent-pipeline)
- API contracts (see C002-data-contracts)
- Data model definitions (locked in LLD)

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-BACKEND-001 | Backend SHALL use 7-layer Clean Architecture | Must |
| FR-BACKEND-002 | Domain entities SHALL use @dataclass with business methods | Must |
| FR-BACKEND-003 | Repository interfaces SHALL be ABC in domain/repositories/ | Must |
| FR-BACKEND-004 | Repository implementations SHALL be in infrastructure/ | Must |
| FR-BACKEND-005 | Application DTOs SHALL be Pydantic v2 models in application/dtos/ | Must |
| FR-BACKEND-006 | Use cases SHALL be single-purpose classes in application/use_cases/ | Must |
| FR-BACKEND-007 | Mappers SHALL use static methods in application/mappers/ | Must |
| FR-BACKEND-008 | All imports SHALL be absolute (no `from .` or `from ..`) | Must |
| FR-BACKEND-009 | No file SHALL exceed 150 lines | Must |
| FR-BACKEND-010 | `agent/` layer SHALL contain DSPy agents, tools, signatures | Must |
| FR-BACKEND-011 | `ui/` layer SHALL contain UI descriptors and WebSocket protocols | Must |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-BACKEND-001 | All code SHALL pass `ruff check --fix` | Must |
| NFR-BACKEND-002 | All code SHALL pass `ruff format` | Must |
| NFR-BACKEND-003 | All code SHALL pass `pyrefly check --summarize-errors` | Must |
| NFR-BACKEND-004 | Each layer SHALL have a README.md explaining its purpose | Should |

## 1.4 Data Model

```python
# Locked from LLD: domain_model.md:38-110
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from typing import Optional

@dataclass
class AgentSessionEntity:
    """Represents a user's conversation session with the AI agent.

    Lifecycle: INITIALIZING -> ACTIVE -> PAUSED/CLOSED
    """
    session_id: UUID
    user_id: str  # SHA-256 hash
    state: SessionState
    created_at: datetime
    modified_at: datetime
    last_activity_at: datetime
    current_reasoning_step: int = 0
    total_tool_calls: int = 0
```

**Placement**: `/home/riju279/Documents/Code/XRIG/AgentX/agentx/domain/entities/agent_session.py`

## 1.5 API Contract

*None for this spec - see C002-data-contracts*

## 1.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-BACKEND-001 | Domain layer has no external dependencies | Code review (no imports from infrastructure/) |
| BR-BACKEND-002 | Infrastructure can import from domain only | Code review |
| BR-BACKEND-003 | Presentation can import from application only | Code review |
| BR-BACKEND-004 | File split at 150 lines | `find agentx/ -name "*.py" -exec wc -l {} +` |

## 1.7 Acceptance Criteria

- [ ] All 7 directories exist with correct subdirectories
- [ ] All entities are @dataclass with business methods
- [ ] All repositories follow ABC pattern
- [ ] All imports are absolute paths
- [ ] No files exceed 150 lines
- [ ] All code passes ruff check, ruff format, pyrefly check
- [ ] Each layer has README.md explaining purpose

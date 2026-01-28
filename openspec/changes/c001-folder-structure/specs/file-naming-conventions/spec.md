# Spec: file-naming-conventions

**File**: `specs/file-naming-conventions/spec.md`

## 1.1 Purpose

Define consistent file naming conventions to avoid the scattered model problems in R014.

## 1.2 Scope

**In Scope**:
- File naming rules for backend
- File placement rules (what goes where)
- Naming patterns to avoid

**Out of Scope**:
- Code style (see CLAUDE_POLICY.md)
- Runtime behavior

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-NAMING-001 | Domain entities SHALL be in `domain/entities/<name>.py` | Must |
| FR-NAMING-002 | Value objects SHALL be in `domain/value_objects/<name>.py` | Must |
| FR-NAMING-003 | Repository interfaces SHALL be in `domain/repositories/<name>_repository.py` | Must |
| FR-NAMING-004 | Request DTOs SHALL be in `application/dtos/requests.py` or `application/dtos/<feature>_requests.py` | Must |
| FR-NAMING-005 | Response DTOs SHALL be in `application/dtos/responses.py` or `application/dtos/<feature>_responses.py` | Must |
| FR-NAMING-006 | Use cases SHALL be in `application/use_cases/<action>_<entity>.py` | Must |
| FR-NAMING-007 | Mappers SHALL be in `application/mappers/<entity>_mapper.py` | Must |
| FR-NAMING-008 | API routes SHALL be in `presentation/api/v1/<feature>_routes.py` | Must |
| FR-NAMING-009 | NEVER create `models.py` or `schemas.py` in service folders | Must |
| FR-NAMING-010 | Entity names SHALL NOT have redundant suffixes (e.g., `widget_id` not `widget_widget_id`) | Should |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-NAMING-001 | Naming conventions enforced via code review | Must |
| NFR-NAMING-002 | No `models.py` or `schemas.py` in service folders (verified by grep) | Must |

## 1.4 Data Model

```python
# Example: Correct placement
# File: domain/entities/agent_session.py
@dataclass
class AgentSessionEntity:
    session_id: UUID
    # Note: NOT widget_session_id (redundant suffix)

# File: application/dtos/requests.py
class ExecuteAgentQueryRequest(BaseModel):
    query: str
    # Note: NOT ExecuteAgentQueryQueryRequest (redundant)
```

## 1.5 API Contract

*None for this spec*

## 1.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-NAMING-001 | No `models.py` in service folders | `grep -r "models.py" agentx/services/` |
| BR-NAMING-002 | No `schemas.py` in service folders | `grep -r "schemas.py" agentx/services/` |
| BR-NAMING-003 | Entities end with `Entity` suffix | Code review |
| BR-NAMING-004 | DTOs end with `DTO` suffix | Code review |
| BR-NAMING-005 | Use cases end with `UseCase` suffix | Code review |

## 1.7 Acceptance Criteria

- [ ] All files follow naming conventions
- [ ] Zero `models.py` files in service folders
- [ ] Zero `schemas.py` files in service folders
- [ ] All data models consolidated to domain/ or application/dtos/
- [ ] Entity/DTO/UseCase/Mapper suffixes used consistently

# Specs Artifact: {{change_name}}

**Generated**: {{timestamp}}
**Change**: {{change_name}}
**Schema**: spec-factory v1.0.0

---

## Spec Structure

This artifact generates domain-specific specification files in `specs/{domain}/spec.md`.

---

## 1. Spec: {{domain_name}}

**File**: `specs/{{domain_name}}/spec.md`

### 1.1 Purpose

<!-- What this domain spec defines -->

### 1.2 Scope

**In Scope**:
- <!-- Scope item 1 -->
- <!-- Scope item 2 -->

**Out of Scope**:
- <!-- Out of scope item 1 -->

### 1.3 Requirements

#### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-{{domain}}-001 | <!-- Requirement --> | Must/Should/Could |

#### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-{{domain}}-001 | <!-- Requirement --> | Must/Should/Could |

### 1.4 Data Model

```python
# Locked from LLD: domain_model.md:XXX
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

@dataclass
class ExampleEntity:
    """Entity description from LLD."""
    entity_id: UUID
    created_at: datetime
    # ... fields from LLD
```

### 1.5 API Contract

#### REST Endpoints

| Method | Path | Request | Response | Status Codes |
|--------|------|---------|----------|--------------|
| <!-- Fill --> | | | | 200, 404, 500 |

#### WebSocket Channels

| Channel | Direction | Message Schema |
|---------|-----------|----------------|
| <!-- Fill --> | | |

### 1.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| <!-- Rule 1 --> | | Code/Config |

### 1.7 Acceptance Criteria

- [ ] <!-- Criterion 1 -->
- [ ] <!-- Criterion 2 -->
- [ ] <!-- Criterion 3 -->

---

## 2. Spec: {{another_domain_name}}

<!-- Repeat for each domain spec needed -->

---

## 3. Cross-Domain Contracts

### 3.1 Shared Types

<!-- Types used across multiple domains -->

### 3.2 Integration Points

| Domain A | Domain B | Interface |
|----------|----------|-----------|
| <!-- Fill --> | | |

---

**Next Artifact**: design.md

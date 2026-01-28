# Extract Artifact: {{change_name}}

**Generated**: {{timestamp}}
**Change**: {{change_name}}
**Schema**: spec-factory v1.0.0

---

## 1. Pattern Catalog

### 1.1 Architectural Patterns

| Pattern | Source | Description | Apply? |
|---------|--------|-------------|--------|
| Clean Architecture | mimicus | Layered separation with domain independence | ✅ |
| Repository Pattern | mimicus | ABC base + implementations | ✅ |
| DTO Pattern | mimicus | Pydantic models for API layer | ✅ |
| <!-- Add more --> | | | |

### 1.2 Code Structure Patterns

| Pattern | Example | Apply? |
|---------|---------|--------|
| @dataclass entities | `class AgentSessionEntity:` | ✅ |
| ABC repositories | `class AgentSessionRepository(ABC):` | ✅ |
| Static mappers | `@staticmethod def to_dto()` | ✅ |
| Use case classes | `class CreateSessionUseCase:` | ✅ |
| <!-- Add more --> | | |

### 1.3 Naming Patterns (to Avoid from R014)

| R014 Name | Why Avoid | Alternative |
|-----------|-----------|-------------|
| <!-- Fill in --> | | |

---

## 2. Specification Drafts

### 2.1 Draft: {{domain}} Spec

**Purpose**: <!-- What this spec defines -->

**Scope**:
- <!-- In scope -->
- <!-- Out of scope -->

**Locked from LLD**:
```python
# Paste locked entity/signature from LLD
```

**Requirements**:
1. <!-- Fill in -->
2. <!-- Fill in -->

**Acceptance Criteria**:
- [ ] <!-- Criterion 1 -->
- [ ] <!-- Criterion 2 -->

---

### 2.2 Draft: {{another_domain}} Spec

<!-- Repeat for each domain spec needed -->

---

## 3. API Contracts

### 3.1 REST Endpoints

| Method | Path | Request | Response |
|--------|------|---------|----------|
| <!-- Fill in --> | | | |

### 3.2 WebSocket Channels

| Channel | Message Type | Schema |
|---------|--------------|--------|
| <!-- Fill in --> | | |

### 3.3 Port Assignments

| Service | Port | Purpose |
|---------|------|---------|
| <!-- Fill in (use 8015+) --> | | |

---

## 4. Data Model Mappings

### 4.1 Pydantic → Zod Mappings

| Pydantic Model | Zod Type | Notes |
|----------------|----------|-------|
| <!-- Fill in --> | | |

### 4.2 Shared Types

<!-- Define types that exist in both backend and frontend -->

```python
# Backend (Pydantic v2)
class ExampleModel(BaseModel):
    field: str
```

```typescript
// Frontend (Zod)
const ExampleModelSchema = z.object({
  field: z.string(),
});
```

---

## 5. Dependencies on Other Specs

| Spec | Dependency Type | Rationale |
|------|-----------------|-----------|
| <!-- Fill in --> | | |

---

**Next Artifact**: validate.md

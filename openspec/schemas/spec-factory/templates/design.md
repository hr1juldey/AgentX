# Design Artifact: {{change_name}}

**Generated**: {{timestamp}}
**Change**: {{change_name}}
**Schema**: spec-factory v1.0.0

---

## 1. Architecture

### 1.1 Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    System Overview                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   ┌─────────┐         ┌─────────┐         ┌─────────┐  │
│   │ Frontend│────────▶│ Backend │────────▶│ Storage │  │
│   │ (Next)  │         │ (Fast)  │         │ (Qdrant)│  │
│   └─────────┘         └─────────┘         └─────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Layer Structure (Clean Architecture)

```
app/
├── core/              # Configuration, dependencies
├── domain/            # Business logic (no external deps)
│   ├── entities/      # @dataclass entities
│   ├── repositories/  # ABC interfaces + implementations
│   └── services/      # Domain services
├── application/       # Use case orchestration
│   ├── use_cases/     # Single-purpose classes
│   ├── dtos/          # Pydantic models
│   └── mappers/       # Entity ↔ DTO
├── infrastructure/    # External concerns
│   └── database/      # DB models
└── presentation/      # FastAPI routes
    └── api/v1/        # REST endpoints
```

---

## 2. Data Flow

### 2.1 Request Flow

```
Client → API → Use Case → Repository → Storage
                ↓           ↓
              DTO        Entity
```

### 2.2 Event Flow (if applicable)

```
Producer → Event Bus → Consumer → Action
```

---

## 3. Technical Decisions

| Decision | Option Chosen | Alternatives | Rationale |
|----------|---------------|--------------|-----------|
| <!-- Decision 1 --> | | | |
| <!-- Decision 2 --> | | | |

---

## 4. Tradeoff Analysis

### 4.1 Approach A: {{Option A}}

| Aspect | Rating | Notes |
|--------|--------|-------|
| Simplicity | ⭐⭐⭐ | |
| Performance | ⭐⭐ | |
| Maintainability | ⭐⭐⭐ | |

**Pros**:
- <!-- Pro 1 -->
- <!-- Pro 2 -->

**Cons**:
- <!-- Con 1 -->
- <!-- Con 2 -->

### 4.2 Approach B: {{Option B}}

| Aspect | Rating | Notes |
|--------|--------|-------|
| Simplicity | ⭐⭐ | |
| Performance | ⭐⭐⭐ | |
| Maintainability | ⭐⭐ | |

**Pros**:
- <!-- Pro 1 -->

**Cons**:
- <!-- Con 1 -->

### 4.3 Decision: {{Chosen Approach}}

**Rationale**: <!-- Why this approach -->

---

## 5. Implementation Details

### 5.1 Key Classes/Modules

| Module | Responsibility | Dependencies |
|--------|----------------|--------------|
| <!-- Module 1 --> | | |

### 5.2 Port Assignments

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| <!-- Service 1 --> | 8015 | HTTP | API |
| <!-- Service 2 --> | 8016 | WS | Streaming |

### 5.3 Storage Schema

```python
# Data model definition
class ExampleModel(BaseModel):
    field: str
```

---

## 6. Security Considerations

| Concern | Mitigation |
|---------|------------|
| <!-- Concern 1 --> | <!-- Mitigation --> |

---

## 7. Performance Considerations

| Concern | Mitigation |
|---------|------------|
| <!-- Concern 1 --> | <!-- Mitigation --> |

---

**Next Artifact**: tasks.md

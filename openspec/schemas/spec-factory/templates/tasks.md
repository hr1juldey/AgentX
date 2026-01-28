# Tasks Artifact: {{change_name}}

**Generated**: {{timestamp}}
**Change**: {{change_name}}
**Schema**: spec-factory v1.0.0

---

## 1. Implementation Checklist

### 1.1 Phase 1: Foundation

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create directory structure | `app/` | ⬜ | Follow Clean Architecture |
| Create core config | `app/core/config.py` | ⬜ | Pydantic Settings |
| Create entities | `app/domain/entities/*.py` | ⬜ | @dataclass, <100 lines |
| Create repositories | `app/domain/repositories/*.py` | ⬜ | ABC + implementations |
| Create use cases | `app/application/use_cases/*.py` | ⬜ | Single-purpose classes |
| Create DTOs | `app/application/dtos/*.py` | ⬜ | Pydantic v2 |
| Create mappers | `app/application/mappers/*.py` | ⬜ | Static methods |
| Create routes | `app/presentation/api/v1/*.py` | ⬜ | FastAPI |

### 1.2 Phase 2: Integration

| Task | File | Status | Notes |
|------|------|--------|-------|
| Wire dependencies | `app/core/dependencies.py` | ⬜ | Singletons |
| Add middleware | `app/core/middleware/*.py` | ⬜ | CORS, logging |
| Connect storage | `app/infrastructure/database/*.py` | ⬜ | Qdrant, Redis |

### 1.3 Phase 3: Frontend

| Task | File | Status | Notes |
|------|------|--------|-------|
| Create types | `frontend/types/*.ts` | ⬜ | Zod schemas |
| Create components | `frontend/components/*.tsx` | ⬜ | <100 lines |
| Create hooks | `frontend/hooks/*.ts` | ⬜ | Custom hooks |
| Wire API client | `frontend/lib/api.ts` | ⬜ | Axios/Fetch |

### 1.4 Phase 4: Testing

| Task | Type | Status | Notes |
|------|------|--------|-------|
| Unit tests | `tests/unit/*.py` | ⬜ | pytest |
| Integration tests | `tests/integration/*.py` | ⬜ | API tests |
| E2E tests | `tests/e2e/*.spec.ts` | ⬜ | Playwright |

---

## 2. Verification Steps

### 2.1 Code Quality

```bash
# Run all quality checks
ruff check app/ --fix
ruff format app/
pyrefly check app/ --summarize-errors
```

### 2.2 File Size Check

```bash
# Verify no file exceeds 150 lines
find app/ -name "*.py" -exec wc -l {} + | awk '$1 > 150'
```

### 2.3 Import Check

```bash
# Verify no relative imports
grep -r "from \.\." app/  # Should return nothing
grep -r "from \." app/ | grep -v "from \.\.\."  # Should return nothing
```

### 2.4 Type Check

```bash
# Frontend type check
cd frontend
npx tsc --noEmit
```

---

## 3. Acceptance Criteria

### 3.1 Functional Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| <!-- Criterion 1 --> | Manual/Auto | <!-- Result --> |

### 3.2 Non-Functional Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| Response time < 200ms | Benchmark | P95 < 200ms |
| Zero relative imports | Grep check | 0 matches |
| All files < 150 lines | WC check | All pass |

---

## 4. Definition of Done

A change is **complete** when:

- [ ] All implementation tasks are done
- [ ] All verification steps pass
- [ ] All acceptance criteria are met
- [ ] Code review approved
- [ ] Tests pass (pytest + E2E)
- [ ] Documentation updated

---

## 5. Rollback Plan

If implementation fails:

1. **Identify failure point**: <!-- Method -->
2. **Rollback steps**:
   - ```bash
     # Rollback commands
     ```
3. **Recovery actions**:
   - <!-- Recovery step 1 -->
   - <!-- Recovery step 2 -->

---

## 6. Dependencies Unlocked

This change unlocks:

| Change | Unlocked Feature |
|--------|-----------------|
| <!-- Next change --> | <!-- Feature --> |

---

**End of spec-factory pipeline**

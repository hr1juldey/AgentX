# Spec: DSPy Caching

**Domain**: dspy_caching
**Generated**: 2026-02-03
**Status**: Draft

---

## 1. Purpose

Enable DSPy caching for performance. Change cache=False to cache=True.

**Problem Statement**: DSPy cache explicitly disabled (Fraud #53). Unnecessary LLM calls.

**Success Criteria**: dspy.py has cache=True in LM configuration.

---

## 2. Scope

### In Scope

- Enable DSPy LM caching
- Change cache=False to cache=True in dspy.py

### Out of Scope

- Cache invalidation (handled by DSPy)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| RF-CACHE-001 | dspy.py has cache=True in LM configuration | Must |

### 3.2 Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-CACHE-001 | File passes Ruff and Pyrefly | Must |

---

## 4. Data Model

```python
# BEFORE - Cache disabled
lm = dspy.LM(
    model=f"ollama_chat/{model}",
    api_base=settings.ollama_base_url,
    cache=False,  # ❌ Disabled
)

# AFTER - Cache enabled
lm = dspy.LM(
    model=f"ollama_chat/{model}",
    api_base=settings.ollama_base_url,
    cache=True,  # ✅ Enabled
)
```

---

## 5. API Contract

This spec modifies configuration only. No REST/WebSocket endpoints.

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-CACHE-001 | cache=True in LM configuration | Code review |

---

## 7. Acceptance Criteria

- [ ] dspy.py has cache=True in LM configuration
- [ ] File passes: `ruff check` and `pyrefly check`
- [ ] Verification passes:
```bash
grep -n "cache=" agentx/core/dependency_facades/dspy.py | grep -i "true"
```

---

## 8. References

- **Fraud #53**: `.claude/fraud/AGENTX_DSPY_FRAUD_ANALYSIS_2026.md` (Cache Disabled)
- **Plan**: `.claude/plans/golden-skipping-hedgehog.md` (Batch 11)

---

**Related Specs**:
- None (single-line change)

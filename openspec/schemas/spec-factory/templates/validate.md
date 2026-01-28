# Validate Artifact: {{change_name}}

**Generated**: {{timestamp}}
**Change**: {{change_name}}
**Schema**: spec-factory v1.0.0

---

## 1. CLAUDE_POLICY.md Compliance

### 1.1 Import Rules

| Check | Status | Evidence |
|-------|--------|----------|
| No relative imports (`from .`) | ⬜/✅/❌ | |
| Absolute imports only | ⬜/✅/❌ | |
| No architectural violations | ⬜/✅/❌ | |

### 1.2 Ruff Compliance

| Check | Status | Evidence |
|-------|--------|----------|
| ruff check --fix passes | ⬜/✅/❌ | |
| ruff format passes | ⬜/✅/❌ | |

### 1.3 File Size Limits

| Check | Status | Evidence |
|-------|--------|----------|
| Max 100 lines executable | ⬜/✅/❌ | |
| Max 50 lines overhead | ⬜/✅/❌ | |

### 1.4 Anti-Patterns

| Anti-Pattern | Present? | Fix Required |
|--------------|----------|--------------|
| God objects | ⬜/✅/❌ | |
| Magic numbers/strings | ⬜/✅/❌ | |
| Circular imports | ⬜/✅/❌ | |
| Import hacks | ⬜/✅/❌ | |

---

## 2. Spec Quality Validation

### 2.1 Completeness

| Element | Present? | Notes |
|---------|----------|-------|
| Clear scope definition | ⬜/✅/❌ | |
| Success criteria | ⬜/✅/❌ | |
| Acceptance criteria | ⬜/✅/❌ | |
| API contracts defined | ⬜/✅/❌ | |
| Data models specified | ⬜/✅/❌ | |

### 2.2 Clarity

| Aspect | Rating | Notes |
|--------|--------|-------|
| Language clarity | 1-5 | |
| Ambiguity level | Low/Med/High | |
| Jargon explained | ⬜/✅/❌ | |

### 2.3 Feasibility

| Aspect | Rating | Notes |
|--------|--------|-------|
| Technical feasibility | 1-5 | |
| Dependencies clear | ⬜/✅/❌ | |
| Implementation path clear | ⬜/✅/❌ | |

---

## 3. Locked Definitions Check

### 3.1 LLD Alignment

| Element | LLD Source | Matches? |
|---------|------------|----------|
| Entity definitions | domain_model.md:XXX | ⬜/✅/❌ |
| Enum values | domain_model.md:XXX | ⬜/✅/❌ |
| Signatures | agent_runtime.md:XXX | ⬜/✅/❌ |
| Repository methods | domain_model.md:XXX | ⬜/✅/❌ |

### 3.2 Deviations from LLD

| Element | LLD Definition | Proposed Deviation | Justification |
|---------|----------------|-------------------|---------------|
| <!-- Fill if any --> | | | |

---

## 4. Required Fixes

### 4.1 Critical Fixes (Must Fix)

| Issue | Location | Fix |
|-------|----------|-----|
| <!-- Fill in --> | | |

### 4.2 Optional Improvements

| Issue | Location | Suggestion |
|-------|----------|------------|
| <!-- Fill in --> | | |

---

## 5. Validation Summary

### 5.1 Overall Status

- **Policy Compliance**: ⬜ PASS / FAIL
- **Spec Quality**: ⬜ PASS / FAIL
- **LLD Alignment**: ⬜ PASS / FAIL
- **Ready for Proposal**: ⬜ YES / NO

### 5.2 Blocking Issues

<!-- List any issues that must be resolved before proceeding -->

1. <!-- Issue 1 -->
2. <!-- Issue 2 -->

---

**Next Artifact**: proposal.md

# Scan Artifact: {{change_name}}

**Generated**: {{timestamp}}
**Change**: {{change_name}}
**Schema**: spec-factory v1.0.0

---

## 1. LLD Synthesis

### 1.1 Relevant LLD Documents

| Document | Path | Relevance |
|----------|------|-----------|
| <!-- Fill in --> | | |

### 1.2 Locked Definitions from LLD

<!-- Extract locked entities, enums, signatures from LLD docs -->

#### Entities
<!-- List @dataclass entities with fields -->

#### Enums
<!-- List enum values -->

#### Signatures
<!-- List DSPy signatures -->

#### Repository Interfaces
<!-- List ABC repository methods -->

---

## 2. Codebase Exploration (opsx:explore)

### 2.1 Exploration Topics

```
<!-- List forced topics for opsx:explore -->
```

### 2.2 File Inventory

#### Backend Files
| File | Lines | Purpose |
|------|-------|---------|
| <!-- Fill in --> | | |

#### Frontend Files
| File | Lines | Purpose |
|------|-------|---------|

---

## 3. Patterns Discovered

### 3.1 Architectural Patterns

<!-- List patterns found: Clean Architecture layers, use cases, etc. -->

### 3.2 Code Patterns

<!-- List implementation patterns: @dataclass, ABC repos, DTOs, etc. -->

### 3.3 Anti-Patterns to Avoid

<!-- List issues found in R014 or prototypes to avoid -->

---

## 4. Reference Analysis

### 4.1 Mimicus Patterns (Copy Concepts, Not Names)

| Concept | Mimicus Pattern | Intended Use |
|---------|-----------------|--------------|
| Clean Architecture | core/, domain/, application/, infrastructure/, presentation/ | | |
| Repository | ABC base class + implementations | | |
| Entity | @dataclass with business methods | | |
| Use Case | Single-purpose classes with execute() | | |

### 4.2 R014 Reference (Concepts Only)

| Concept | R014 Approach | Improved Approach |
|---------|---------------|-------------------|
| <!-- Fill in --> | | |

---

## 5. Key Files for This Change

<!-- List absolute paths to key files for this specific change -->

```
/home/riju279/Documents/Code/XRIG/AgentX/...
```

---

**Next Artifact**: extract.md

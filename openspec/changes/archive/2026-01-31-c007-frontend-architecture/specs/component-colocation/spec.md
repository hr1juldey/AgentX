# Spec: component-colocation

**File**: `specs/component-colocation/spec.md`

## 1.1 Purpose

Define the component colocation strategy where ui.tsx widget registries are placed next to graph.py backend code.

## 1.2 Scope

**In Scope**:
- ui.tsx placement (same directory as graph.py)
- Widget registry format (default export with component map)
- Absolute import paths (`@/agent/ui`)

**Out of Scope**:
- Widget component implementations (handled by C008, C009)

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-CC-001 | ui.tsx MUST be in same directory as graph.py | Must |
| FR-CC-002 | Widget registry MUST use default export | Must |
| FR-CC-003 | Component paths MUST use absolute imports | Must |

## 1.4 Acceptance Criteria

- [ ] ui.tsx exists next to graph.py
- [ ] Widget registry uses default export
- [ ] All imports use absolute paths

# Spec: flat-design

**File**: `specs/flat-design/spec.md`

## 1.1 Purpose

Define the flat design system that removes gradients, uses subtle borders, and creates consistent visual surfaces.

## 1.2 Scope

**In Scope**:
- Flat header pattern (remove gradients)
- Subtle border system (1px, low opacity)
- Surface layering (void → membrane → cytoplasm → organelle)

**Out of Scope**:
- Shadow system (already defined in C008 tokens.shadow)
- Motion animations (handled by C008 motion presets)

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-FD-001 | Headers MUST use flat backgrounds (`bg-organelle`) | Must |
| FR-FD-002 | Headers MUST use subtle borders (`border-b border-white/[0.06]`) | Must |
| FR-FD-003 | No gradients allowed (`bg-gradient-to-*` prohibited) | Must |
| FR-FD-004 | Surface layering MUST follow void → membrane → cytoplasm → organelle | Must |
| FR-FD-005 | Depth created via shadows, not gradients | Must |

## 1.4 Acceptance Criteria

- [ ] All headers use flat backgrounds
- [ ] All headers use subtle borders
- [ ] No gradients found in codebase
- [ ] Surface layering consistent
- [ ] Depth created via shadows

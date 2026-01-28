# Spec: spacing-tokens

**File**: `specs/spacing-tokens/spec.md`

## 1.1 Purpose

Ensure all spacing uses token-based values instead of arbitrary numbers for consistent layout.

## 1.2 Scope

**In Scope**:
- Padding (p-* classes)
- Margin (m-* classes)
- Gap (gap-* classes for flex/grid)

**Out of Scope**:
- Component-specific spacing (handled by component props)
- Responsive spacing (handled by Tailwind responsive variants)

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-ST-001 | All padding MUST use spacing tokens | Must |
| FR-ST-002 | All margin MUST use spacing tokens | Must |
| FR-ST-003 | All gap MUST use spacing tokens | Must |
| FR-ST-004 | No arbitrary spacing values (p-4, m-6, gap-2 prohibited) | Must |

## 1.4 Acceptance Criteria

- [ ] All padding uses spacing tokens
- [ ] All margin uses spacing tokens
- [ ] All gap uses spacing tokens
- [ ] No arbitrary spacing found

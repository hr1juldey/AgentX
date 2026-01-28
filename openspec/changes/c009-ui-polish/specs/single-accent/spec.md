# Spec: single-accent

**File**: `specs/single-accent/spec.md`

## 1.1 Purpose

Define the single accent color system that standardizes all interactive elements to use one consistent accent color (enzyme/cyan).

## 1.2 Scope

**In Scope**:
- Primary actions (buttons, links, interactive elements)
- Icon colors (success, info, warning → all use enzyme)
- Focus indicators (ring, outline)
- Active states (selected, pressed)

**Out of Scope**:
- Semantic colors (mitosis green, apoptosis red) - already defined in C008
- Text hierarchy (nucleus, protein, ghost) - already defined in C008

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-SA-001 | All interactive elements MUST use `text-enzyme` or `bg-enzyme` | Must |
| FR-SA-002 | Secondary elements MUST use `text-ghost` (not green/gray/blue) | Must |
| FR-SA-003 | Focus indicators MUST use `ring-enzyme` | Must |
| FR-SA-004 | Active states MUST use enzyme variant (enzymeSoft, enzymeGlow) | Must |
| FR-SA-005 | No mixed icon colors (all icons use enzyme or ghost) | Must |

## 1.4 Acceptance Criteria

- [ ] All interactive elements use enzyme color
- [ ] All secondary elements use ghost color
- [ ] No mixed icon colors
- [ ] Focus indicators use enzyme ring
- [ ] Active states use enzyme variants

# Spec: widget-protocol

**File**: `specs/widget-protocol/spec.md`

## 1.1 Purpose

Define the widget protocol that specifies the 12 widget types and their props interfaces.

## 1.2 Scope

**In Scope**:
- 12 widget type definitions
- Widget props interfaces
- Widget name freezing rules

**Out of Scope**:
- Widget component implementations (handled by C008, C009)

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-WP-001 | Frontend MUST support 12 widget types | Must |
| FR-WP-002 | Widget names MUST match backend `push_ui_message()` calls | Must |

## 1.4 Widget Types

```typescript
type WidgetType =
  | 'markdown'
  | 'card'
  | 'form'
  | 'progress'
  | 'action'
  | 'confirmation'
  | 'image'
  | 'gallery'
  | 'chart'
  | 'searchResult'
  | 'hopProgress'
  | 'citationCard'
```

## 1.5 Acceptance Criteria

- [ ] All 12 widget types defined
- [ ] Widget names frozen after Phase 7
- [ ] Frontend and backend widget names match

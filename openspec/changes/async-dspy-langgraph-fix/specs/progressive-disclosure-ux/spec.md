# Spec: Progressive Disclosure UX

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Draft

---

## 1. Purpose

Define the progressive disclosure UX pattern for widgets (3 visible, "Show More" button).

**Success Criteria**:
- ProgressiveDisclosure component shows 3 widgets initially
- "Show More" button appears when > 3 widgets
- Widgets sorted by priority (highest first)
- WidgetRevealEvent for each widget

---

## 2. Scope

### In Scope

- ProgressiveDisclosure frontend component
- ShowMoreButton component
- Widget sorting by priority
- WidgetRevealEvent emission

### Out of Scope

- Widget selection logic (covered by content-pattern-detection spec)
- Widget components (DataTable, Timeline, Map, etc.)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-PDU-001 | ProgressiveDisclosure MUST show 3 widgets initially | Must |
| FR-PDU-002 | ShowMoreButton MUST appear when > 3 widgets | Must |
| FR-PDU-003 | Widgets MUST sort by priority | Should |
| FR-PDU-004 | WidgetRevealEvent MUST emit for each widget | Should |

---

## 4. Frontend Components

```typescript
// frontend/components/ProgressiveDisclosure.tsx
import { useState } from "react";

interface Widget {
  widget_type: string;
  title: string;
  content: any;
  priority: number;
}

export function ProgressiveDisclosure({ widgets }: { widgets: Widget[] }) {
  const [showAll, setShowAll] = useState(false);
  const maxVisible = 3;

  // Sort by priority (highest first)
  const sortedWidgets = [...widgets].sort((a, b) => b.priority - a.priority);

  const visibleWidgets = showAll ? sortedWidgets : sortedWidgets.slice(0, maxVisible);
  const hasMore = widgets.length > maxVisible;

  return (
    <div className="widgets-container">
      {visibleWidgets.map((widget, index) => (
        <div
          key={index}
          className="widget-item"
          style={{ order: -widget.priority }}  // Higher priority first
        >
          <WidgetCard widget={widget} />
        </div>
      ))}

      {hasMore && !showAll && (
        <button
          onClick={() => setShowAll(true)}
          className="show-more-button"
        >
          Show {widgets.length - maxVisible} More Widgets
        </button>
      )}
    </div>
  );
}

// frontend/components/ShowMoreButton.tsx
export function ShowMoreButton({ count, onClick }: { count: number, onClick: () => void }) {
  return (
    <button onClick={onClick} className="show-more-button">
      Show {count} More Widgets
    </button>
  );
}

// frontend/components/WidgetCard.tsx
export function WidgetCard({ widget }: { widget: any }) {
  switch (widget.widget_type) {
    case "data_table":
      return <DataTable {...widget.content} title={widget.title} />;
    case "chart":
      return <Chart {...widget.content} title={widget.title} />;
    case "timeline":
      return <Timeline {...widget.content} title={widget.title} />;
    default:
      return <TextCard {...widget.content} title={widget.title} />;
  }
}
```

---

## 5. Backend Support

```python
# agent/nodes/synthesizer.py

async def synthesizer_node(state: AgentState) -> AsyncGenerator[dict, None]:
    """Synthesize response with progressive disclosure."""
    findings = state.get("research_findings", [])
    widgets = state.get("selected_widgets", [])

    # Phase 1: Stream text response
    for chunk in stream_synthesizer(query=query, findings=findings):
        yield {"streaming_event": TokenEvent(token=chunk)}

    # Phase 2: Reveal widgets progressively (highest priority first)
    widgets.sort(key=lambda w: w.priority, reverse=True)

    for i, widget in enumerate(widgets):
        yield {
            "streaming_event": WidgetRevealEvent(
                widget=widget,
                index=i,
                total=len(widgets),
            ),
        }

    # Phase 3: Final completion
    yield {
        "final_response": final_response,
        "widgets": widgets,
        "widget_count": len(widgets),
    }
```

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-PDU-001 | 3 visible initially | maxVisible = 3 |
| BR-PDU-002 | Priority sort | sort((a, b) => b.priority - a.priority) |
| BR-PDU-003 | Button only if > 3 | hasMore check |

---

## 7. Acceptance Criteria

- [ ] ProgressiveDisclosure component created
- [ ] Shows 3 widgets initially
- [ ] "Show More" button appears when > 3
- [ ] Clicking shows all widgets
- [ ] Widgets sorted by priority
- [ ] WidgetRevealEvent emitted
- [ ] TypeScript compiles

---

## 8. Test Scenarios

| Widget Count | Expected Display |
|--------------|-----------------|
| 0 | No widgets, no button |
| 2 | 2 widgets, no button |
| 3 | 3 widgets, no button |
| 5 | 3 widgets + "Show 2 More" button |
| 10 | 3 widgets + "Show 7 More" button |

---

**Next**: See `content-pattern-detection/spec.md` for widget selection logic.

# Spec: Adaptive Widget Selection

**Domain**: agent-runtime
**Generated**: 2026-02-01
**Status**: Draft

---

## 1. Purpose

Define the adaptive widget selection system that dynamically generates UI components based on query complexity and accumulated research findings. This replaces R014's "arbitrary widget dump" with intelligent, content-driven widget selection.

**Problem Statement**: R014 sends maximum types and numbers of widgets no matter what happens, resulting in irrelevant UI clutter and poor user experience. Users see widgets for data that wasn't found or isn't relevant to their query.

**Success Criteria**:
- Only relevant widgets are generated based on actual findings
- Widget selection adapts to query complexity (simple queries get minimal UI)
- Widget types match content types (comparison → table, timeline → chart, etc.)
- No "widget dump" - each widget serves a clear purpose

---

## 2. Scope

### In Scope

- Dynamic widget selection based on accumulated state
- Widget type inference from content patterns
- Widget count limits based on query complexity
- Integration with synthesizer node for widget generation
- Frontend widget components (React/Next.js)

### Out of Scope

- Widget component implementation details (see frontend specs)
- Voice UI patterns (see C010 voice client)
- Transient UX streaming (see transient-ux spec)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-AWS-001 | Analyze accumulated findings for widget candidates | Must | Content-driven |
| FR-AWS-002 | Infer widget types from content patterns | Must | Auto-detection |
| FR-AWS-003 | Limit widget count based on query complexity | Should | Prevent clutter |
| FR-AWS-004 | Simple queries (0 tasks) get text-only response | Must | Minimal UI |
| FR-AWS-005 | Complex queries get relevant widgets only | Must | No dump |
| FR-AWS-006 | Widget selection uses structured output | Must | No parsing |
| FR-AWS-007 | Widgets include source attribution | Should | Transparency |
| FR-AWS-008 | Widgets support progressive disclosure | Should | Prevent overwhelm |

### 3.2 Non-Functional Requirements

| ID | Requirement | Priority | Target Metric |
|----|-------------|----------|---------------|
| NFR-AWS-001 | Widget selection latency | Must | < 500ms |
| NFR-AWS-002 | Max widgets per response | Should | 3-7 widgets |
| NFR-AWS-003 | Simple query widget count | Must | 0-1 widgets |
| NFR-AWS-004 | Widget generation accuracy | Should | >90% relevant |

---

## 4. Data Model

### 4.1 Widget Types

```python
# domain/models/widgets.py
from pydantic import BaseModel, Field
from typing import Literal, Optional, Any
from enum import Enum

class WidgetType(str, Enum):
    """Types of widgets that can be generated."""
    TEXT_CARD = "text_card"           # Simple text content
    SUMMARY_CARD = "summary_card"     # Summary with key points
    DATA_TABLE = "data_table"         # Comparison data
    CHART = "chart"                   # Bar/line/pie chart
    IMAGE_CARD = "image_card"         # Visual content
    LINK_LIST = "link_list"           # Source links
    MAP = "map"                       # Geographic data
    TIMELINE = "timeline"             # Historical events
    CODE_BLOCK = "code_block"         # Code snippets
    QUOTE_CARD = "quote_card"         # Quotes/statements
    LIST_CARD = "list_card"           # Bulleted/numbered lists

class ChartType(str, Enum):
    """Types of charts."""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"

class ContentPattern(BaseModel):
    """Pattern detected in content that suggests a widget type."""
    pattern_type: Literal[
        "comparison",          # "Compare X vs Y" → DATA_TABLE
        "ranking",             # "Top 10..." → DATA_TABLE or CHART
        "temporal",            # "History of..." → TIMELINE or CHART
        "geographic",          # "Where is...", "Map of..." → MAP
        "numerical",           # Contains statistics → CHART
        "categorical",         # Multiple categories → DATA_TABLE
        "visual",              # Describes images → IMAGE_CARD
        "code",                # Code snippets → CODE_BLOCK
        "quotations",          # Quotes from sources → QUOTE_CARD
        "list",                # Multiple items → LIST_CARD
    ]
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in pattern detection")
    evidence: str = Field(description="Why this pattern was detected")

class WidgetSpecification(BaseModel):
    """Specification for a single widget."""
    widget_type: WidgetType = Field(description="Type of widget to render")
    title: str = Field(description="Widget title")
    content: dict[str, Any] = Field(description="Widget-specific content data")
    priority: float = Field(ge=0.0, le=1.0, description="Display priority (higher = more important)")
    sources: list[str] = Field(default_factory=list, description="Source URLs/refs")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional widget metadata")

# Widget-specific content models
class DataTableContent(BaseModel):
    """Content for DATA_TABLE widget."""
    columns: list[str] = Field(description="Column headers")
    rows: list[list[str]] = Field(description="Data rows")
    caption: Optional[str] = Field(default=None, description="Table caption")

class ChartContent(BaseModel):
    """Content for CHART widget."""
    chart_type: ChartType
    x_axis: str = Field(description="X-axis label")
    y_axis: str = Field(description="Y-axis label")
    data_points: list[dict[str, float]] = Field(description="Data points")
    labels: list[str] = Field(description="Data point labels")

class TimelineContent(BaseModel):
    """Content for TIMELINE widget."""
    events: list[dict] = Field(description="Timeline events with date, title, description")
    start_date: Optional[str] = Field(default=None, description="Timeline start")
    end_date: Optional[str] = Field(default=None, description="Timeline end")

class MapContent(BaseModel):
    """Content for MAP widget."""
    locations: list[dict] = Field(description="Locations with lat, lng, label")
    center_lat: float = Field(description="Map center latitude")
    center_lng: float = Field(description="Map center longitude")
    zoom: int = Field(default=10, ge=1, le=20, description="Map zoom level")

class ImageCardContent(BaseModel):
    """Content for IMAGE_CARD widget."""
    image_url: str = Field(description="Image URL")
    caption: Optional[str] = Field(default=None, description="Image caption")
    alt_text: str = Field(description="Alt text for accessibility")

class CodeBlockContent(BaseModel):
    """Content for CODE_BLOCK widget."""
    code: str = Field(description="Code snippet")
    language: str = Field(description="Programming language")
    caption: Optional[str] = Field(default=None, description="Code caption")

class QuoteCardContent(BaseModel):
    """Content for QUOTE_CARD widget."""
    quotes: list[dict] = Field(description="Quotes with text, source, context")
    attribution: str = Field(description="Overall attribution")

class ListCardContent(BaseModel):
    """Content for LIST_CARD widget."""
    items: list[str] = Field(description="List items")
    list_type: Literal["bulleted", "numbered"] = Field(default="bulleted")
    title: Optional[str] = Field(default=None, description="List title")

class WidgetSelectionResult(BaseModel):
    """Result of widget selection process."""
    widgets: list[WidgetSpecification] = Field(description="Selected widgets (sorted by priority)")
    total_count: int = Field(description="Total widgets selected")
    rationale: str = Field(description="Why these widgets were selected")
    skipped_patterns: list[ContentPattern] = Field(default_factory=list, description="Patterns detected but skipped")
```

### 4.2 Widget Selection State

```python
# agent/state/widget_state.py
from typing import Annotated
from operator import add

class WidgetState(TypedDict):
    """State for widget selection (part of AgentState)."""

    # Input for widget selection
    accumulated_findings: list[str]  # Research findings
    query_type: Literal["simple", "complex"]  # From query planner
    execution_plan: ExecutionPlan  # Original plan

    # Widget selection results
    selected_widgets: list[WidgetSpecification]
    widget_patterns: list[ContentPattern]  # All detected patterns
    widget_count: int  # Final count (after filtering)

    # Widget generation status
    widgets_generated: bool
    generation_duration_ms: float
```

---

## 5. API Contract

### 5.1 DSPy Widget Selection Module

```python
# agent/tools/widgets/widget_selector.py
import dspy
from dspy import InputField, OutputField, Signature

class SelectWidgetsSignature(dspy.Signature):
    """Select appropriate widgets based on accumulated findings."""

    original_query = InputField(desc="User's original query")
    accumulated_findings = InputField(desc="All research findings gathered")
    query_complexity = InputField(desc="Query complexity (simple or complex)")
    max_widgets = InputField(desc="Maximum number of widgets to select")

    # Structured output (JSON)
    selected_widgets = OutputField(desc="JSON array of widget specifications")
    rationale = OutputField(desc="Why these widgets were selected")
    total_count = OutputField(desc="Number of widgets selected")

class WidgetSelectorModule(dspy.Module):
    """Select widgets based on content analysis."""

    def __init__(self):
        super().__init__()
        self.select = dspy.Predict(SelectWidgetsSignature)

    def forward(
        self,
        original_query: str,
        accumulated_findings: list[str],
        query_complexity: Literal["simple", "complex"],
        max_widgets: int = 5,
    ) -> dspy.Prediction:
        """Select appropriate widgets."""

        findings_text = "\n\n".join(accumulated_findings)

        result = self.select(
            original_query=original_query,
            accumulated_findings=findings_text,
            query_complexity=query_complexity,
            max_widgets=str(max_widgets),
        )

        # Parse structured output
        widgets = self._parse_widgets(result.selected_widgets)

        return dspy.Prediction(
            selected_widgets=widgets,
            rationale=result.rationale,
            total_count=int(result.total_count),
        )

    def _parse_widgets(self, widgets_json: str) -> list[WidgetSpecification]:
        """Parse JSON output into WidgetSpecification objects."""
        import json

        widgets_data = json.loads(widgets_json)
        return [WidgetSpecification(**w) for w in widgets_data]

    async def aforward(
        self,
        original_query: str,
        accumulated_findings: list[str],
        query_complexity: Literal["simple", "complex"],
        max_widgets: int = 5,
    ) -> dspy.Prediction:
        """Async widget selection."""
        return await self.select.acall(
            original_query=original_query,
            accumulated_findings="\n\n".join(accumulated_findings),
            query_complexity=query_complexity,
            max_widgets=str(max_widgets),
        )
```

### 5.2 Widget Generator Node

```python
# agent/nodes/widget_generator.py
from agent.tools.widgets.widget_selector import WidgetSelectorModule
from domain.models.widgets import WidgetSpecification, WidgetSelectionResult

async def widget_generator_node(state: AgentState) -> dict:
    """Generate widgets based on accumulated findings.

    This runs AFTER the evaluator decides to finalize.
    Simple queries (0 tasks) skip widget generation.
    """

    query = state["query"]
    findings = state.get("research_findings", [])
    plan = state["execution_plan"]

    # Simple queries with no research get text-only response
    if len(plan.research_tasks) == 0:
        return {
            "selected_widgets": [],
            "widgets_generated": False,
            "generation_duration_ms": 0,
        }

    # Determine max widgets based on complexity
    task_count = len(plan.research_tasks)
    if task_count <= 2:
        max_widgets = 2
    elif task_count <= 5:
        max_widgets = 4
    else:
        max_widgets = 7

    start_time = time.perf_counter()

    # Select widgets using DSPy
    selector = WidgetSelectorModule()
    result = await selector.aforward(
        original_query=query,
        accumulated_findings=findings,
        query_complexity="complex" if task_count > 0 else "simple",
        max_widgets=max_widgets,
    )

    duration_ms = (time.perf_counter() - start_time) * 1000

    # Parse and validate widgets
    widgets: list[WidgetSpecification] = result.selected_widgets

    # Sort by priority
    widgets.sort(key=lambda w: w.priority, reverse=True)

    return {
        "selected_widgets": widgets,
        "widget_count": len(widgets),
        "widgets_generated": True,
        "generation_duration_ms": duration_ms,
        "execution_path": ["widget_generator"],
    }
```

### 5.3 Synthesizer Integration

```python
# agent/nodes/synthesizer.py
from typing import AsyncGenerator

async def synthesizer_node(state: AgentState) -> AsyncGenerator[dict, None]:
    """Synthesize final response with widgets.

    This node generates both:
    1. Text response (streaming)
    2. Widget specifications (structured)
    """

    findings = state.get("research_findings", [])
    query = state["query"]
    widgets = state.get("selected_widgets", [])

    # 1. Generate text response (streaming)
    response_parts = []
    for i, chunk in enumerate(stream_synthesizer(query=query, findings=findings)):
        response_parts.append(chunk)
        yield {
            "streaming_event": TokenEvent(
                token=chunk,
                is_first=(i == 0),
                index=i,
            ),
        }

    final_response = "".join(response_parts)

    # 2. Include widgets in final output
    yield {
        "final_response": final_response,
        "widgets": widgets,
        "widget_count": len(widgets),
        "streaming_event": CompleteEvent(
            final_response=final_response,
            duration_ms=duration_ms,
            metadata={
                "widget_count": len(widgets),
                "widget_types": [w.widget_type for w in widgets],
            },
        ),
    }
```

---

## 6. Business Rules

| Rule | Description | Enforcement | Source |
|------|-------------|-------------|--------|
| BR-AWS-001 | Simple queries (0 tasks) get no widgets | Widget generator check | Minimal UI |
| BR-AWS-002 | Max widgets based on task count | Dynamic limit calculation | Prevent clutter |
| BR-AWS-003 | Widgets sorted by priority | Sort before output | Most important first |
| BR-AWS-004 | Each widget needs clear purpose | LLM evaluates relevance | No dump |
| BR-AWS-005 | Widgets include source attribution | Required field | Transparency |
| BR-AWS-006 | No duplicate widget types | Deduplication logic | Avoid redundancy |

---

## 7. Widget Type Inference Rules

### 7.1 Pattern → Widget Mapping

| Content Pattern | Widget Type | Trigger | Example |
|-----------------|-------------|---------|---------|
| `comparison` | DATA_TABLE | "Compare", "vs", "versus" | "Compare iPhone 15 vs Pixel 8" |
| `ranking` | DATA_TABLE or CHART | "Top", "Best", "Worst", "Rank" | "Top 10 smartphones 2024" |
| `temporal` | TIMELINE or CHART (line) | "History", "Timeline", "Evolution" | "History of the iPhone" |
| `geographic` | MAP | "Where", "Location", "Map", "Place" | "Where is Tesla manufactured?" |
| `numerical` | CHART | Statistics, percentages, metrics | "Market share by OS" |
| `categorical` | DATA_TABLE | Multiple categories with attributes | "Phone specs comparison" |
| `visual` | IMAGE_CARD | Describes images, photos, diagrams | "Show me the design" |
| `code` | CODE_BLOCK | Code snippets, commands, functions | "How to parse JSON in Python" |
| `quotations` | QUOTE_CARD | Quotes from sources, interviews | "What did Elon Musk say?" |
| `list` | LIST_CARD | Multiple items, steps, options | "Steps to reset iPhone" |

### 7.2 Widget Count Limits

| Task Count | Max Widgets | Rationale |
|------------|-------------|-----------|
| 0 (simple query) | 0 | Direct answer, no research needed |
| 1-2 (light research) | 2-3 | Minimal findings, focused UI |
| 3-5 (moderate research) | 4-5 | Balanced UI |
| 6+ (deep research) | 6-7 | Rich findings, comprehensive UI |

---

## 8. Acceptance Criteria

- [ ] Simple queries (0 tasks) return no widgets
- [ ] Complex queries return relevant widgets only
- [ ] Widget types match content patterns
- [ ] Max widget count enforced based on task count
- [ ] Widgets sorted by priority
- [ ] Each widget includes source attribution
- [ ] No duplicate widget types
- [ ] Widget selection < 500ms
- [ ] Ruff and pyrefly checks pass

---

## 9. Test Scenarios

### 9.1 Simple Query (No Widgets)

| Query | Tasks | Expected Widgets |
|-------|-------|------------------|
| "What is 2+2?" | 0 | None (text-only) |
| "What's the capital of France?" | 0 | None (direct answer) |

### 9.2 Comparison Query (Table Widget)

| Query | Pattern | Expected Widgets |
|-------|---------|-----------------|
| "Compare iPhone 15 vs Pixel 8" | comparison | 1 DATA_TABLE with specs |
| "Top 5 laptops 2024" | ranking | 1 DATA_TABLE or CHART |

### 9.3 Temporal Query (Timeline/Chart)

| Query | Pattern | Expected Widgets |
|-------|---------|-----------------|
| "History of the iPhone" | temporal | 1 TIMELINE or LINE_CHART |
| "Apple stock price 2024" | temporal + numerical | 1 LINE_CHART |

### 9.4 Geographic Query (Map Widget)

| Query | Pattern | Expected Widgets |
|-------|---------|-----------------|
| "Where are Tesla factories?" | geographic | 1 MAP with locations |

### 9.5 Code Query (Code Block Widget)

| Query | Pattern | Expected Widgets |
|-------|---------|-----------------|
| "How to parse JSON in Python" | code | 1 CODE_BLOCK |

---

## 10. Frontend Integration

### 10.1 Widget Rendering Component

```typescript
// frontend/components/WidgetRenderer.tsx
import { DataTable, Chart, Timeline, Map, CodeBlock, QuoteCard, ListCard } from './widgets';

interface WidgetRendererProps {
  widgets: WidgetSpecification[];
}

export function WidgetRenderer({ widgets }: WidgetRendererProps) {
  if (widgets.length === 0) {
    return null; // Simple query, no widgets
  }

  return (
    <div className="widgets-container">
      {widgets.map((widget, index) => (
        <div key={index} className="widget-item" style={{ order: -widget.priority }}>
          <WidgetCard widget={widget} />
        </div>
      ))}
    </div>
  );
}

function WidgetCard({ widget }: { widget: WidgetSpecification }) {
  switch (widget.widget_type) {
    case 'data_table':
      return <DataTable {...widget.content} title={widget.title} sources={widget.sources} />;
    case 'chart':
      return <Chart {...widget.content} title={widget.title} sources={widget.sources} />;
    case 'timeline':
      return <Timeline {...widget.content} title={widget.title} sources={widget.sources} />;
    case 'map':
      return <Map {...widget.content} title={widget.title} sources={widget.sources} />;
    case 'code_block':
      return <CodeBlock {...widget.content} title={widget.title} sources={widget.sources} />;
    case 'quote_card':
      return <QuoteCard {...widget.content} title={widget.title} sources={widget.sources} />;
    case 'list_card':
      return <ListCard {...widget.content} title={widget.title} sources={widget.sources} />;
    default:
      return <TextCard {...widget.content} title={widget.title} sources={widget.sources} />;
  }
}
```

### 10.2 Progressive Disclosure

```typescript
// frontend/components/ProgressiveDisclosure.tsx
import { useState } from 'react';

export function ProgressiveDisclosure({ widgets }: { widgets: WidgetSpecification[] }) {
  const [showAll, setShowAll] = useState(false);
  const maxVisible = 3;

  const visibleWidgets = showAll ? widgets : widgets.slice(0, maxVisible);
  const hasMore = widgets.length > maxVisible;

  return (
    <div>
      <WidgetRenderer widgets={visibleWidgets} />

      {hasMore && !showAll && (
        <button onClick={() => setShowAll(true)}>
          Show {widgets.length - maxVisible} More Widgets
        </button>
      )}
    </div>
  );
}
```

---

## 11. Comparison to R014

| Aspect | R014 | New Design |
|--------|------|------------|
| **Widget count** | Always max (arbitrary dump) | Adaptive (0-7 based on findings) |
| **Widget selection** | Static, predefined | Dynamic, content-driven |
| **Relevance** | Often irrelevant | Only relevant widgets |
| **Simple queries** | Still gets widgets | No widgets (text-only) |
| **Source attribution** | Missing | Included |
| **User control** | None | Progressive disclosure |

---

## 12. References

- **R014 Analysis**: Fixed pipeline, arbitrary widget dump
- **Query Planner**: Provides task count for widget limits
- **Synthesizer**: Integrates widget generation with response
- **Transient UX**: Widget rendering with streaming
- **Frontend**: Widget components (DataTable, Chart, Timeline, Map, etc.)

---

**Next**: See `transient-ux/spec.md` for widget rendering patterns with streaming.

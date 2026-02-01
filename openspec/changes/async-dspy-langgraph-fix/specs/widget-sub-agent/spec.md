# Spec: Widget Sub-Agent

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Draft

---

## 1. Purpose

Define the Widget sub-agent with exactly 3 tools for UI widget generation.

**Success Criteria**:
- WidgetAgent has exactly 3 tools
- Tools: select_widgets, render_card, show_chart
- Uses accumulated_findings for content-driven selection
- Returns dspy.Prediction

---

## 2. Scope

### In Scope

- WidgetAgent DSPy class
- 3 tools for widget operations
- Content-driven widget selection
- Progressive disclosure support

### Out of Scope

- Widget selection logic (covered by content-pattern-detection spec)
- Widget rendering (frontend layer)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-WSA-001 | WidgetAgent MUST have exactly 3 tools | Must |
| FR-WSA-002 | MUST use accumulated_findings for selection | Must |
| FR-WSA-003 | MUST return dspy.Prediction | Must |
| FR-WSA-004 | Adaptive widget count based on findings | Should |

---

## 4. API Contract

```python
# agent/react_agents/widget_agent.py
import dspy
from dspy import Tool

# Tool wrappers
from agent.tools.widgets.widget_selector import select_widgets
from agent.tools.widgets.card_renderer import render_card
from agent.tools.widgets.chart_renderer import show_chart

class WidgetAgent(dspy.Module):
    """Widget generation specialist with ONLY 3 tools.

    Prevents arbitrary widget dump by:
    - Content-driven selection
    - Adaptive count based on findings
    """

    def __init__(self):
        super().__init__()

        # 🔴 CRITICAL: Only 3 tools
        tools = [
            Tool(select_widgets, name="select_widgets"),
            Tool(render_card, name="render_card"),
            Tool(show_chart, name="show_chart"),
        ]

        self.react = dspy.ReAct(
            "query, accumulated_findings -> widget_plan",
            tools=tools,
            max_iters=2,
        )

    def forward(
        self,
        query: str,
        accumulated_findings: list[str] = [],
    ) -> dspy.Prediction:
        """Generate adaptive widgets based on findings.

        Args:
            query: User's query
            accumulated_findings: Research findings (required!)

        Returns:
            dspy.Prediction: With selected_widgets, widget_count
        """
        findings_text = "\n".join(accumulated_findings)

        result = self.react(
            query=query,
            accumulated_findings=findings_text,
        )

        return dspy.Prediction(
            selected_widgets=result.selected_widgets,
            widget_count=len(result.selected_widgets),
        )
```

---

## 5. Tool Definitions

```python
# agent/tools/widgets/widget_selector.py
def select_widgets(
    query: str,
    accumulated_findings: str,
) -> list[dict]:
    """Select appropriate widgets based on findings.

    Args:
        query: User's query
        accumulated_findings: All research findings

    Returns:
        list[dict]: Widget specifications
    """
    # Content-driven selection logic
    pass

# agent/tools/widgets/card_renderer.py
def render_card(title: str, content: str) -> dict:
    """Render a card widget.

    Args:
        title: Card title
        content: Card content

    Returns:
        dict: Widget specification
    """
    return {
        "widget_type": "card",
        "title": title,
        "content": content,
    }

# agent/tools/widgets/chart_renderer.py
def show_chart(data: str, chart_type: str) -> dict:
    """Show a chart widget.

    Args:
        data: Chart data
        chart_type: Type of chart

    Returns:
        dict: Widget specification
    """
    return {
        "widget_type": "chart",
        "data": data,
        "chart_type": chart_type,
    }
```

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-WSA-001 | No findings = no widgets | Empty list returned |
| BR-WSA-002 | Max 7 widgets | select_widgets enforces |
| BR-WSA-003 | Content-driven | findings required |

---

## 7. Acceptance Criteria

- [ ] WidgetAgent has exactly 3 tools
- [ ] Uses accumulated_findings for selection
- [ ] Returns dspy.Prediction (not dict)
- [ ] Adaptive count based on findings
- [ ] Ruff and pyrefly checks pass

---

## 8. Test Scenarios

| Findings Count | Expected Widgets |
|---------------|-----------------|
| 0 | 0 widgets |
| 1-2 | 1-2 widgets |
| 6+ | 6-7 widgets (max) |

---

**Next**: See `content-pattern-detection/spec.md` for pattern detection logic.

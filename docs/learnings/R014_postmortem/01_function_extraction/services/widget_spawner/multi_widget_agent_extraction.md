# multi_widget_agent.py - Function Extraction

## File: services/widget_spawner/multi_widget_agent.py

### Primary Purpose
DSPy ReAct agent for spawning multiple widgets based on user query - automatically decides which widgets to create.

### Key Classes

#### `MultiWidgetSpawnerAgent(dspy.Module)`
**Purpose**: DSPy ReAct agent for spawning multiple widgets.

**ReAct signature**: `"user_query -> widget_results: list[str]"`

**Tools**: `WIDGET_TOOLS` (from tools module)

**Max iterations**: 10 (configurable)

**Workflow**:
1. Analyze query to understand what information is needed
2. Call appropriate widget generation tools (can call multiple)
3. Aggregate results from all tool calls
4. Return list of generated widgets

**Output format**:
- `widget_results`: List of JSON strings like `{"widget": {...}, "tool_used": "..."}`
- Each widget result is parsed into WidgetDescriptor

**Example scenarios**:
- "Show me EV sales with a summary" → chart widget + markdown widget
- "Create a signup form with terms" → form widget + card widget
- "Track download progress with action buttons" → progress widget + action widget

---

### Key Methods

#### `forward(user_query: str) -> dspy.Prediction`
**Purpose**: Generate one or more widget descriptors based on user query.

**Returns**: dspy.Prediction with:
- `widgets`: List of WidgetDescriptor objects
- `tools_used`: List of tool names called
- `reasoning`: ReAct reasoning trace (if available)
- `trajectory`: ReAct trajectory (if available)

**Error handling**: Skips invalid widget results (JSON parse errors).

---

### Architectural Patterns

1. **ReAct pattern**: LLM automatically decides which tools to call
2. **Multi-widget output**: Can generate multiple widgets in one call
3. **Tool aggregation**: Combines results from multiple tool calls
4. **Error tolerance**: Skips invalid results instead of crashing

---

### Dependencies

**Internal**:
- `services.widget_spawner.models`: WidgetDescriptor
- `services.widget_spawner.tools`: WIDGET_TOOLS

**External**:
- `dspy`: DSPy framework
- `json`: JSON parsing

---

### Lessons Learned

1. **ReAct enables multi-widget**: LLM can call multiple tools in one query
2. **JSON wrapping**: Tool results wrapped in `{"widget": ..., "tool_used": ...}`
3. **Error tolerance**: Skip invalid results, don't fail entire request
4. **Reasoning trace**: ReAct provides visibility into decision making
5. **Tool flexibility**: Can call any combination of tools based on query

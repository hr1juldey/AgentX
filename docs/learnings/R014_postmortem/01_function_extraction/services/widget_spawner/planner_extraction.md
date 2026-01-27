# planner.py - Function Extraction

## File: services/widget_spawner/planner.py

### Primary Purpose
DSPy agent for planning WHAT widgets to generate based on user query (not HOW to generate them).

### DSPy Classes

#### `PlanWidgetsSignature(dspy.Signature)`
**Purpose**: DSPy signature for widget planning.

**Widget Selection Guide** (from docstring):
- `"markdown"`: Reports, documents, text, articles, guides, explanations, summaries
- `"card"`: Highlights, key points, facts, notifications, simple information
- `"form"`: ONLY for data collection - input forms, surveys, feedback (NOT for presenting information)
- `"progress"`: Status, progress, loading state, completion percentage
- `"chart"`: Graphs, plots, visualizations, data viz, statistics, trends
- `"action"`: Buttons, actions, triggers, execute operations
- `"confirmation"`: Confirm dialogs, yes/no prompts, approve/reject
- `"image"`: Pictures, photos, graphics, visual content
- `"gallery"`: Multiple images, image collection, photo gallery

**Inputs**:
- `user_query`: User's query or request
- `available_widgets`: List of available widget types

**Outputs**:
- `widget_plan`: JSON array of widget plans with type and context

**Example output**:
```json
[
  {"type": "chart", "context": "EV sales data by year"},
  {"type": "markdown", "context": "Summary of trends"}
]
```

---

#### `WidgetPlannerAgent(dspy.Module)`
**Purpose**: DSPy agent for planning what widgets to generate.

**Responsibilities**:
- Analyzes user intent
- Decides which widgets are needed
- Provides context for each widget

**NOT responsibilities**:
- Does NOT generate widget content (executor's job)

**JSON parsing**:
- Strips markdown code blocks (```)
- Validates plan structure
- Adds default type/context if missing
- Falls back to single markdown widget on parse error

---

### Architectural Patterns

1. **Separation of concerns**: Planner decides WHAT, executor generates HOW
2. **JSON parsing with fallback**: Strips markdown, validates, falls back
3. **Detailed docstring guidance**: LLM needs explicit examples
4. **Error recovery**: Parse errors don't crash - use fallback

---

### Dependencies

**Internal**:
- `services.widget_spawner.config`: AVAILABLE_WIDGET_TYPES

**External**:
- `dspy`: DSPy framework
- `json`: JSON parsing
- `logging`: Standard logging

---

### Lessons Learned

1. **Clear separation**: Planner decides WHAT, executor generates HOW
2. **Strip markdown**: LLMs wrap JSON in ``` blocks - strip them
3. **Validate structure**: Ensure plan has required fields
4. **Fallback is critical**: Parse errors shouldn't crash the system
5. **Explicit guidance**: LLM needs detailed examples in docstring
6. **Forms are NOT for presenting**: Emphasize forms are only for data collection

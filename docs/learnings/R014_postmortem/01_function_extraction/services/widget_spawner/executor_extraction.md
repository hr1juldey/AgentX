# executor.py - Function Extraction

## File: services/widget_spawner/executor.py

### Primary Purpose
Execute widget plan and generate actual widgets based on plan from planner.

### Key Classes

#### `WidgetExecutorAgent`
**Purpose**: Execute a widget plan and generate all widgets.

**Responsibilities**:
- Takes plan from planner (NOT decide what to create)
- Generates each widget with its specific context
- Returns complete list of generated widgets

**NOT responsibilities**:
- Does NOT decide what widgets to create (planner's job)

---

### DSPy Predictors

**Initialized in `__init__`**:
- `self.markdown_generator = dspy.Predict(GenerateMarkdownSignature)`
- `self.card_generator = dspy.Predict(GenerateCardSignature)`
- `self.form_generator = dspy.Predict(GenerateFormSignature)`
- `self.progress_generator = dspy.Predict(GenerateProgressSignature)`
- `self.chart_generator = dspy.Predict(GenerateChartSignature)`

**Other tools**:
- `self.image_search = SearXNGSearchModule()`

---

### Builder Registries

#### `_dspy_builders` (requires DSPy)
```python
{
    "markdown": (markdown_generator, build_markdown_widget),
    "card": (card_generator, build_card_widget),
    "form": (form_generator, build_form_widget),
    "progress": (progress_generator, build_progress_widget),
    "chart": (chart_generator, build_chart_widget),
}
```

#### `_simple_builders` (no DSPy)
```python
{
    "action": build_action_widget,
    "confirmation": build_confirmation_widget,
}
```

---

### Key Methods

#### `execute_plan(plan: list[dict]) -> list[WidgetDescriptor]`
**Purpose**: Execute a widget plan and generate all widgets.

**Plan format**: `[{type: str, context: str}, ...]`

**Logic**:
1. Iterate through plan items
2. For each item, generate widget using `_generate_widget()`
3. Catch exceptions and continue (don't fail entire plan)

**Returns**: List of generated WidgetDescriptor objects.

---

#### `_generate_widget(widget_type: str, context: str) -> WidgetDescriptor`
**Purpose**: Generate a single widget.

**Special cases**:
- `image`: Uses helper function (general + image search)
- `gallery`: Uses helper function (general + image search)
- `dspy_builders`: Generate content with DSPy, then build widget
- `simple_builders`: Build widget directly (no DSPy)
- `fallback`: Unknown types become markdown widgets

**Returns**: WidgetDescriptor object.

---

### Architectural Patterns

1. **Separation of concerns**: Planner decides, executor generates
2. **Builder registry**: Maps widget types to (generator, builder) pairs
3. **Exception tolerance**: Continue on failure - don't lose all widgets
4. **Fallback strategy**: Unknown types default to markdown
5. **DSP vs simple**: Some widgets need LLM, some don't

---

### Dependencies

**Internal**:
- `services.tools.researcher.searxng_search`: SearXNGSearchModule
- `services.widget_spawner.builders`: build_*_widget functions
- `services.widget_spawner.executor_helpers`: generate_*_widget helpers
- `services.widget_spawner.models`: WidgetDescriptor
- `services.widget_spawner.signatures`: Generate*Signature classes

**External**:
- `dspy`: DSPy framework
- `logging`: Standard logging
- `uuid`: Widget ID generation

---

### Lessons Learned

1. **Separate planning from execution**: Planner decides WHAT, executor generates HOW
2. **Builder registry pattern**: Clean mapping of widget types to generators
3. **Exception tolerance**: One widget failure shouldn't break entire plan
4. **DSPy vs simple**: Not all widgets need LLM - action/confirmation are static
5. **Image widgets are special**: Need both general and image search
6. **Fallback is critical**: Unknown widget types should default, not crash

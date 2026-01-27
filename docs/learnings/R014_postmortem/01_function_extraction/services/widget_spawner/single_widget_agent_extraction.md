# single_widget_agent.py - Function Extraction

## File: services/widget_spawner/single_widget_agent.py

### Primary Purpose
Fallback agent for single widget generation (legacy behavior) - selects and generates one widget.

### Key Classes

#### `SingleWidgetSpawnerAgent(dspy.Module)`
**Purpose**: Fallback agent for single widget generation.

**Use cases**:
- Force a specific widget type
- Simpler fallback when multi-widget is not needed

**DSPy predictors**:
- `widget_selector`: Selects widget type based on query
- `markdown_generator`, `card_generator`, `form_generator`, `progress_generator`, `chart_generator`: Generate content

**Builder registry** (`_builders`):
- Maps widget types to (generator, builder) tuples
- Some widgets have DSPy generators, others don't
- Action, confirmation, image, gallery: no DSPy generator (simple builders)

---

### Key Methods

#### `forward(user_query: str, widget_type: str | None = None) -> dspy.Prediction`
**Purpose**: Generate a single widget descriptor.

**Logic**:
1. If widget_type not provided, use widget_selector to choose
2. Generate unique widget_id
3. Get (generator, builder) from registry
4. If generator exists: Generate content with DSPy, then build widget
5. If no generator: Build widget directly (no DSPy)
6. Return prediction with single widget

**Error handling**: Raises ValueError for unknown widget types.

**Returns**: dspy.Prediction with:
- `widgets`: List with single WidgetDescriptor
- `selected_widget`: Selected widget type

---

### Architectural Patterns

1. **Two-stage generation**: Select type → Generate content → Build widget
2. **Builder registry**: Maps widget types to (generator, builder) pairs
3. **Optional DSPy**: Some widgets need LLM, some are static
4. **Fallback pattern**: Simpler than multi-widget for basic use cases

---

### Dependencies

**Internal**:
- `services.widget_spawner.builders`: build_*_widget functions
- `services.widget_spawner.config`: AVAILABLE_WIDGET_TYPES
- `services.widget_spawner.models`: WidgetDescriptor
- `services.widget_spawner.signatures`: Select*Signature, Generate*Signature classes

**External**:
- `dspy`: DSPy framework
- `uuid`: Widget ID generation

---

### Lessons Learned

1. **Single widget is simpler**: Sometimes you only need one widget
2. **Selection vs generation**: Two steps - choose type, then generate content
3. **Not all widgets need DSPy**: Action/confirmation are static, no LLM needed
4. **Builder registry pattern**: Clean mapping of widget types to implementations
5. **Forced widget type**: Can override selection by passing widget_type param

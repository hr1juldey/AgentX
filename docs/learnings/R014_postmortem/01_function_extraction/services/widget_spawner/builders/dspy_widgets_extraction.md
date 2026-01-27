# dspy_widgets.py - Function Extraction

## File: services/widget_spawner/builders/dspy_widgets.py

### Primary Purpose
Helper functions for building widget data from DSPy results - converts DSPy outputs to widget descriptors.

### Key Functions

#### `build_markdown_widget(result: GenerateMarkdownSignature, widget_id: str) -> dict`
**Purpose**: Build markdown widget data from DSPy result.

**Fields**:
- `id`: widget_id
- `type`: "markdown"
- `title`: None
- `content`: result.markdown_content
- `metadata`: None
- `timestamp`: Current UTC datetime
- `dismissible`: True

---

#### `build_card_widget(result: GenerateCardSignature, widget_id: str) -> dict`
**Purpose**: Build card widget data from DSPy result.

**Fields**:
- `id`, `type`: "card"
- `title`: result.card_title
- `content`: result.card_content
- `metadata`: {"actions": DEFAULT_CARD_ACTIONS}
- `timestamp`, `dismissible`

---

#### `build_form_widget(result: GenerateFormSignature, widget_id: str) -> dict`
**Purpose**: Build form widget data from DSPy result.

**JSON parsing**: Parses result.form_fields_json, falls back to DEFAULT_FORM_FIELDS on error.

**Fields**:
- `id`, `type`: "form"
- `title`: DEFAULT_FORM_TITLE
- `content`: None
- `metadata`: {"fields": fields, "submit_label": DEFAULT_FORM_SUBMIT_LABEL}
- `timestamp`, `dismissible`

---

#### `build_progress_widget(result: GenerateProgressSignature, widget_id: str) -> dict`
**Purpose**: Build progress widget data from DSPy result.

**Fields**:
- `id`, `type`: "progress"
- `title`: result.task_name
- `content`: None
- `metadata`: {"value": progress_percent / 100, "status_text": result.status_text}
- `timestamp`, `dismissible`

---

#### `build_chart_widget(result: GenerateChartSignature, widget_id: str) -> dict`
**Purpose**: Build chart widget data from DSPy result.

**JSON parsing**:
- Strips markdown code blocks (``` ... ```)
- Falls back to DEFAULT_CHART_DATA on parse error

**Data key extraction**:
- Excludes label keys: year, month, name, label, category, date
- Finds numeric keys (int/float values)
- Falls back to DEFAULT_CHART_DATA_KEYS if none found

**Fields**:
- `id`, `type`: "chart"
- `title`: result.chart_title
- `content`: "Generated chart visualization"
- `metadata`: {"chart_type": result.chart_type, "data": chart_data, "data_keys": data_keys}
- `timestamp`, `dismissible`

---

### Architectural Patterns

1. **Builder functions**: Convert DSPy results to widget descriptors
2. **JSON parsing with fallback**: Handle LLM JSON errors gracefully
3. **Default values**: Use config defaults when parsing fails
4. **Timestamp inclusion**: All widgets have UTC timestamp
5. **Dismissible by default**: All widgets can be closed

---

### Dependencies

**Internal**:
- `services.widget_spawner.config`: All DEFAULT_* constants
- `services.widget_spawner.signatures`: Generate*Signature classes

**External**:
- `json`: JSON parsing
- `datetime`: Timestamp generation
- `typing`: Type hints

---

### Lessons Learned

1. **Strip markdown from JSON**: LLMs wrap JSON in ``` blocks
2. **Fallback on parse errors**: Use defaults instead of crashing
3. **Extract data keys intelligently**: Exclude label keys, find numeric keys
4. **All widgets need timestamps**: Track when widget was created
5. **Dismissible is user-friendly**: Let users close widgets

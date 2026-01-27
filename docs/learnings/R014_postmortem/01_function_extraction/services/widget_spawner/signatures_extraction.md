# signatures.py - Function Extraction

## File: services/widget_spawner/signatures.py

### Primary Purpose
DSPy signatures for widget generation - defines input/output contracts.

### Key Signatures

#### `SelectWidgetSignature(dspy.Signature)`
**Purpose**: Select appropriate UI widget type based on user query intent.

**Inputs**:
- `user_query`: User's query or request
- `available_widgets`: List of available widget types

**Outputs**:
- `selected_widget`: Selected widget type
- `widget_rationale`: Brief explanation of why this widget was chosen

**Widget types**:
- markdown, card, chart, form (data collection ONLY), progress, action, confirmation, image/gallery

**Critical guidance**: Use 'form' ONLY when collecting user input, NOT for presenting research.

---

#### `GenerateMarkdownSignature(dspy.Signature)`
**Purpose**: Generate markdown content for a markdown widget.

**Inputs**:
- `user_query`: User's query or request

**Outputs**:
- `markdown_content`: Generated markdown content

---

#### `GenerateCardSignature(dspy.Signature)`
**Purpose**: Generate title and content for a card widget.

**Inputs**:
- `user_query`: User's query or request

**Outputs**:
- `card_title`: Card title
- `card_content`: Card content (markdown supported)

---

#### `GenerateFormSignature(dspy.Signature)`
**Purpose**: Generate form schema for user input.

**Inputs**:
- `user_query`: User's query or request

**Outputs**:
- `form_fields_json`: JSON array of form fields with name, type, label, required

---

#### `GenerateProgressSignature(dspy.Signature)`
**Purpose**: Generate progress indicator data.

**Inputs**:
- `user_query`: User's query or request

**Outputs**:
- `task_name`: Task name
- `progress_percent`: Progress percentage (0-100)
- `status_text`: Status text description

---

#### `GenerateChartSignature(dspy.Signature)`
**Purpose**: Generate chart data and configuration for visualization.

**Inputs**:
- `user_query`: User's query or request

**Outputs**:
- `chart_type`: Chart type (bar, line, pie, or area)
- `chart_title`: Chart title
- `chart_data_json`: Valid JSON array of chart data points (NO markdown code blocks)

**Critical**: Output MUST be valid JSON only, no markdown formatting.

---

### Architectural Patterns

1. **Signature pattern**: Each widget type has its own signature
2. **Explicit constraints**: Signatures specify output format requirements
3. **Reused guidance**: SelectWidgetSignature has detailed widget type guidance

---

### Dependencies

**Internal**:
- None (signature definitions only)

**External**:
- `dspy`: DSPy framework

---

### Lessons Learned

1. **One signature per widget type**: Clear separation of concerns
2. **Explicit format requirements**: Tell LLM "NO markdown" for JSON fields
3. **Reused guidance**: Widget type explanation in SelectWidgetSignature
4. **Form warning**: Emphasize forms are for data collection only

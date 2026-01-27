# Function Postmortem: services/tools/hydrators/widget_signatures.py

## Metadata
- **File**: services/tools/hydrators/widget_signatures.py
- **Lines of Code**: 86
- **Purpose**: DSPy signatures for card, form, markdown widget hydration
- **Dependencies**: dspy

---

## Analysis

**File Status**: PRODUCTION DSPy SIGNATURES

**Purpose**: Defines DSPy signatures for generating UI widget data (cards, forms, markdown, POVs).

---

## Signatures Extracted

### CardData

**Purpose**: Generate card widget data displaying key metrics and information.

**Lines**: 12-21

**Key Code**:
```python
class CardData(dspy.Signature):
    """Generate card widget data displaying key metrics and information."""

    query = dspy.InputField(desc="User query topic")
    data = dspy.InputField(desc="Research data with key_facts, trends")
    design = dspy.InputField(desc="Color scheme and styling preferences")

    cards = dspy.OutputField(
        desc="JSON array of card objects with title, value, description, icon, and color"
    )
```

**What Works**:
- ✅ Includes design input for styling
- ✅ Output format: JSON array with title, value, description, icon, color
- ✅ Uses key_facts and trends from research data

**Behavioral Notes**:
- Cards are for displaying metrics (key_facts) and trends
- Design controls color scheme for theming

---

### FormFieldNames

**Purpose**: Extract field names for data collection form based on research insights.

**Lines**: 24-33

**Key Code**:
```python
class FormFieldNames(dspy.Signature):
    """Extract field names for a data collection form based on research insights."""

    query = dspy.InputField(desc="User query topic")
    data = dspy.InputField(desc="Research data with collection methodology")
    insights = dspy.InputField(desc="Insights about what data to collect")

    field_names = dspy.OutputField(
        desc="JSON array of field name strings (2-5 words each)"
    )
```

**What Works**:
- ✅ 2-step form generation (names first, then details)
- ✅ insights input guides field selection
- ✅ Constraint: 2-5 words per field name

**Behavioral Notes**:
- First step in form generation pipeline
- Outputs field names only (not types or descriptions)

---

### FormFieldDetails

**Purpose**: Determine field type, description, and options for a single form field.

**Lines**: 36-49

**Key Code**:
```python
class FormFieldDetails(dspy.Signature):
    """Determine field type, description, and options for a single form field."""

    field_name = dspy.InputField(desc="Name of the field")
    query = dspy.InputField(desc="User query topic")
    data = dspy.InputField(desc="Research data for context")

    field_type = dspy.OutputField(
        desc="Input type: text, textarea, number, select, or checkbox"
    )
    description = dspy.OutputField(desc="Help text explaining what to enter")
    options = dspy.OutputField(
        desc="For select: JSON array of options. For other types: empty JSON array"
    )
```

**What Works**:
- ✅ Enumerated field types (text, textarea, number, select, checkbox)
- ✅ Takes single field_name (called iteratively)
- ✅ options conditional: array for select, empty for others
- ✅ description provides UX guidance

**Behavioral Notes**:
- Second step in form generation pipeline
- Called once per field_name from FormFieldNames
- field_type determines whether options are populated

---

### MarkdownContent

**Purpose**: Generate markdown content from research data with proper formatting.

**Lines**: 52-62

**Key Code**:
```python
class MarkdownContent(dspy.Signature):
    """Generate markdown content from research data with proper formatting."""

    query = dspy.InputField(desc="User query topic")
    data = dspy.InputField(desc="Research data with beautiful_data, structured_report")
    povs = dspy.InputField(desc="Points of view to incorporate")
    citations = dspy.InputField(desc="Citations to include")

    markdown_content = dspy.OutputField(
        desc="Markdown formatted content with headings, bullet points, and numbered lists"
    )
```

**What Works**:
- ✅ Incorporates multiple inputs (data, povs, citations)
- ✅ Output format: Markdown with headings, bullets, numbered lists
- ✅ Uses beautiful_data and structured_report

**Behavioral Notes**:
- Combines research data with perspectives (POVs)
- Citations ensure attribution

---

### POVGeneration

**Purpose**: Generate multiple balanced points of view from research data.

**Lines**: 65-73

**Key Code**:
```python
class POVGeneration(dspy.Signature):
    """Generate multiple balanced points of view from research data."""

    query = dspy.InputField(desc="User query topic")
    research_data = dspy.InputField(desc="Research data to analyze")

    points_of_view = dspy.OutputField(
        desc="JSON array of 3-5 perspectives (bullish, bearish, neutral, alternative, skeptical)"
    )
```

**What Works**:
- ✅ Enumerated POV types (bullish, bearish, neutral, alternative, skeptical)
- ✅ Constraint: 3-5 perspectives
- ✅ Balanced perspectives (not biased)

**Behavioral Notes**:
- Outputs structured perspectives for balanced analysis
- Used by MarkdownContent and other widgets

---

### WidgetInsights

**Purpose**: Generate insights specific to widget types from research data.

**Lines**: 76-85

**Key Code**:
```python
class WidgetInsights(dspy.Signature):
    """Generate insights specific to widget types from research data."""

    query = dspy.InputField(desc="User query topic")
    data = dspy.InputField(desc="Research data")
    widget_type = dspy.InputField(desc="Type of widget: card, form, chart, markdown")

    insights = dspy.OutputField(
        desc="JSON array of 3-5 insights specific to the widget type"
    )
```

**What Works**:
- ✅ widget_type input customizes insights
- ✅ Constraint: 3-5 insights
- ✅ Widget-specific (not generic insights)

**Behavioral Notes**:
- Used to generate context-aware insights per widget
- widget_type affects insight focus (e.g., trends for cards, methodology for forms)

---

## File Summary

**Total Signatures**: 6
**Lines of Code**: 86

**Overall Assessment**: Well-designed signature suite for widget generation. 2-step form generation (FormFieldNames → FormFieldDetails) is a key pattern. POVGeneration ensures balanced perspectives.

**Key Learnings for Real AgentX**:
1. ✅ 2-step generation: FormFieldNames (list) → FormFieldDetails (per-item) for complex objects
2. ✅ Enumerated types: Limited field types, chart types, POV types keep output predictable
3. ✅ Design input: Include styling preferences for theming
4. ✅ Perspective diversity: POVGeneration ensures balanced analysis
5. ✅ Widget-specific insights: Customize insights per widget type
6. ✅ Constraints in desc: "2-5 words", "3-5 perspectives" guide LLM output

**Reuse for Real AgentX**: ✅ DIRECT - All signatures are reusable for any UI generation system.

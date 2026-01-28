# dspy_signatures.py - R014 Postmortem Extraction

**File**: `/prototypes/R014_ui_showcase/backend/api/dspy_signatures.py`
**Lines**: 99
**Purpose**: DSPy signatures for content generation

---

## Complete Code Analysis

### File Structure

```python
# =============================================================================
# AGENTX R014 - DSPy Signatures
# =============================================================================
# DSPy signatures for content generation
# =============================================================================

import dspy

class MarkdownContentSignature(dspy.Signature):
    """Generate markdown content."""
    topic = dspy.InputField(desc="Topic to write about")
    content = dspy.OutputField(desc="Markdown formatted content")

class CardContentSignature(dspy.Signature):
    """Generate card content."""
    topic = dspy.InputField(desc="Card topic")
    title = dspy.OutputField(desc="Card title")
    content = dspy.OutputField(desc="Card body content")

class WeatherCardSignature(dspy.Signature):
    """Generate weather card content."""
    location = dspy.InputField(desc="City name")
    weather_info = dspy.OutputField(desc="Weather description with emojis")

class SearchResultsSignature(dspy.Signature):
    """Generate search results."""
    query = dspy.InputField(desc="Search query")
    results = dspy.OutputField(desc="List of search results as numbered items")

class FormFieldsSignature(dspy.Signature):
    """Generate form fields description."""
    form_purpose = dspy.InputField(desc="What the form is for")
    fields_description = dspy.OutputField(desc="Form fields needed")

class FormContentSignature(dspy.Signature):
    """Generate full form content."""
    form_type = dspy.InputField(desc="Type of form (login, feedback, survey, etc.)")
    title = dspy.OutputField(desc="Form title")
    description = dspy.OutputField(desc="Form description")

class ProgressContentSignature(dspy.Signature):
    """Generate progress status."""
    task = dspy.InputField(desc="Task being performed")
    status_text = dspy.OutputField(desc="Current status message")

class ActionContentSignature(dspy.Signature):
    """Generate action button text."""
    action_type = dspy.InputField(desc="Type of action (approve, delete, submit, etc.)")
    button_text = dspy.OutputField(desc="Button label")
    description = dspy.OutputField(desc="Action description")

class ConfirmationContentSignature(dspy.Signature):
    """Generate confirmation dialog."""
    action = dspy.InputField(desc="Action to confirm")
    title = dspy.OutputField(desc="Dialog title")
    message = dspy.OutputField(desc="Confirmation message")

class ImageContentSignature(dspy.Signature):
    """Generate image widget content."""
    subject = dspy.InputField(desc="Image subject or theme")
    title = dspy.OutputField(desc="Image title")
    caption = dspy.OutputField(desc="Image caption or description")

class GalleryContentSignature(dspy.Signature):
    """Generate gallery widget content."""
    theme = dspy.InputField(desc="Gallery theme")
    title = dspy.OutputField(desc="Gallery title")
    description = dspy.OutputField(desc="Gallery description")

class ChartContentSignature(dspy.Signature):
    """Generate chart widget content."""
    data_topic = dspy.InputField(desc="Chart data topic")
    title = dspy.OutputField(desc="Chart title")
    description = dspy.OutputField(desc="Chart description")
```

---

## Signature Catalog

| Signature | Input Fields | Output Fields | Used By |
|-----------|-------------|---------------|---------|
| `MarkdownContentSignature` | topic | content | TextWidgetGenerator.generate_markdown |
| `CardContentSignature` | topic | title, content | TextWidgetGenerator.generate_card |
| `WeatherCardSignature` | location | weather_info | **UNUSED** |
| `SearchResultsSignature` | query | results | **UNUSED** |
| `FormFieldsSignature` | form_purpose | fields_description | **UNUSED** |
| `FormContentSignature` | form_type | title, description | TextWidgetGenerator.generate_form |
| `ProgressContentSignature` | task | status_text | InteractiveWidgetGenerator.generate_progress |
| `ActionContentSignature` | action_type | button_text, description | InteractiveWidgetGenerator.generate_action |
| `ConfirmationContentSignature` | action | title, message | InteractiveWidgetGenerator.generate_confirmation |
| `ImageContentSignature` | subject | title, caption | MediaWidgetGenerator.generate_image |
| `GalleryContentSignature` | theme | title, description | MediaWidgetGenerator.generate_gallery |
| `ChartContentSignature` | data_topic | title, description | MediaWidgetGenerator.generate_chart |

---

## Analysis

### DSPy Signature Pattern

**Structure**:
```python
class SignatureName(dspy.Signature):
    """Docstring describing purpose."""
    input_field = dspy.InputField(desc="Verbose description for LLM")
    output_field = dspy.OutputField(desc="Verbose description for LLM")
```

**What Works**:
- ✅ Verbose field descriptions (good LLM context)
- ✅ Clear naming convention
- ✅ Docstrings for each signature
- ✅ Consistent pattern

**Issues**:
- ⚠️ **3 UNUSED signatures** (WeatherCard, SearchResults, FormFields)
- ⚠️ High similarity between signatures (potential for consolidation)
- ⚠️ No base signature or shared patterns
- ⚠️ Field descriptions could be more specific

### CLAUDE_POLICY.md Compliance

| Check | Status | Notes |
|-------|--------|-------|
| Absolute imports | ✅ Pass | `import dspy` |
| File size | ✅ Pass | 99 lines (<150 limit) |
| No relative imports | ✅ Pass | None used |
| Ruff compliance | ✅ Pass | Clean code |

### DRY Violations

| Pattern | Occurrences | Could Consolidate |
|---------|-------------|-------------------|
| `title = dspy.OutputField(desc="... title")` | 7 | Generic signature |
| `description = dspy.OutputField(desc="... description")` | 6 | Generic signature |
| Single output content | 2 | Generic signature |

---

## Signature Similarity Analysis

### Group 1: Single Output (Content Only)

```python
MarkdownContentSignature: topic -> content
WeatherCardSignature: location -> weather_info
SearchResultsSignature: query -> results
ProgressContentSignature: task -> status_text
```

**Could consolidate to**:
```python
class SingleOutputSignature(dspy.Signature):
    input_prompt = dspy.InputField(desc="Input prompt")
    output_content = dspy.OutputField(desc="Generated content")
```

### Group 2: Title + Description

```python
ImageContentSignature: subject -> title, caption
GalleryContentSignature: theme -> title, description
ChartContentSignature: data_topic -> title, description
```

**Could consolidate to**:
```python
class TitledContentSignature(dspy.Signature):
    subject = dspy.InputField(desc="Content subject or theme")
    title = dspy.OutputField(desc="Content title")
    description = dspy.OutputField(desc="Content description")
```

### Group 3: Unused (Should Remove)

```python
WeatherCardSignature  # No weather integration
SearchResultsSignature  # Not used (search uses different pattern)
FormFieldsSignature  # FormContent used instead
```

---

## Refactoring Needed

### YES - Consolidation

```python
# Proposed: Generic signature with configurable context
class ContentGenerationSignature(dspy.Signature):
    """Generate content for UI widgets."""
    
    context = dspy.InputField(
        desc="Generation context (topic, subject, action, etc.)"
    )
    widget_type = dspy.InputField(
        desc="Type of widget to generate (markdown, card, form, etc.)"
    )
    
    # Standard outputs
    title = dspy.OutputField(desc="Widget title (if applicable)", default=None)
    content = dspy.OutputField(desc="Widget content or description")
    metadata = dspy.OutputField(
        desc="Additional widget-specific data (JSON string)", 
        default=None
    )
```

This replaces 9 signatures with 1 generic signature.

### NO - Keep Separate

- `ActionContentSignature` and `ConfirmationContentSignature` are distinct enough

---

## Behavioral Notes

### LLM Interactions

- Each signature defines input/output contract for LLM
- DSPy maps these to Ollama API calls
- Field descriptions guide LLM output format

### Unused Signatures

1. **WeatherCardSignature**: Never implemented
   - Would need weather API integration
   - Not in scope for R014

2. **SearchResultsSignature**: Not used
   - Search uses different pattern (multi-hop DSPy agent)
   - Should be removed

3. **FormFieldsSignature**: Not used
   - FormContentSignature used instead
   - Should be removed

---

## Lessons Learned

### What Works

- Verbose field descriptions improve LLM output
- Consistent naming convention
- Clear input/output separation

### What Doesn't Work

- **Too many similar signatures** - Maintenance burden
- **Unused code** - WeatherCard, SearchResults, FormFields
- **No base patterns** - Each signature defined from scratch

### Should Copy

- DSPy signature pattern (it's the right approach)
- Verbose descriptions for LLM context
- Clear naming convention

### Should Avoid

- Creating 12 signatures when 3-4 would suffice
- Leaving unused signatures in codebase
- Defining similar signatures without base class

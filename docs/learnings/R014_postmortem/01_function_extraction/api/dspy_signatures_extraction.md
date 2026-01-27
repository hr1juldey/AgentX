# Function Postmortem: api/dspy_signatures.py

## Metadata
- **File**: prototypes/R014_ui_showcase/backend/api/dspy_signatures.py
- **Lines of Code**: 99
- **Purpose**: DSPy signatures for content generation
- **Dependencies**: dspy

---

## Analysis

**Status**: Complete DSPy signature definitions for all widget types

**Purpose**: Defines DSPy Signatures that specify input/output contracts for LLM calls. Each signature corresponds to a widget type.

**Architecture**: DSPy Signature pattern - declarative I/O contracts

---

## Functions/Classes Extracted

### MarkdownContentSignature (dspy.Signature)

**Purpose**: Generate markdown content from topic

**Lines**: 10-14

```python
class MarkdownContentSignature(dspy.Signature):
    topic = dspy.InputField(desc="Topic to write about")
    content = dspy.OutputField(desc="Markdown formatted content")
```

**Reusability**: HIGH - Generic text generation signature

---

### CardContentSignature (dspy.Signature)

**Purpose**: Generate card content with title and body

**Lines**: 17-22

```python
class CardContentSignature(dspy.Signature):
    topic = dspy.InputField(desc="Card topic")
    title = dspy.OutputField(desc="Card title")
    content = dspy.OutputField(desc="Card body content")
```

**Reusability**: HIGH - Good for any card widget

---

### WeatherCardSignature (dspy.Signature)

**Purpose**: Generate weather card with emojis

**Lines**: 25-29

```python
class WeatherCardSignature(dspy.Signature):
    location = dspy.InputField(desc="City name")
    weather_info = dspy.OutputField(desc="Weather description with emojis")
```

**Behavioral Notes**: Specialized card type - could use generic CardContentSignature instead

**Reusability**: LOW - Too specific

---

### SearchResultsSignature (dspy.Signature)

**Purpose**: Generate search results as list

**Lines**: 32-36

```python
class SearchResultsSignature(dspy.Signature):
    query = dspy.InputField(desc="Search query")
    results = dspy.OutputField(desc="List of search results as numbered items")
```

**Reusability**: HIGH - Useful for search features

---

### FormFieldsSignature (dspy.Signature)

**Purpose**: Generate form fields description

**Lines**: 39-43

```python
class FormFieldsSignature(dspy.Signature):
    form_purpose = dspy.InputField(desc="What the form is for")
    fields_description = dspy.OutputField(desc="Form fields needed")
```

**Reusability**: MEDIUM - Specific to forms

---

### FormContentSignature (dspy.Signature)

**Purpose**: Generate full form with title and description

**Lines**: 46-52

```python
class FormContentSignature(dspy.Signature):
    form_type = dspy.InputField(desc="Type of form (login, feedback, survey, etc.)")
    title = dspy.OutputField(desc="Form title")
    description = dspy.OutputField(desc="Form description")
```

**Reusability**: HIGH - Good for any form type

---

### ProgressContentSignature (dspy.Signature)

**Purpose**: Generate progress status message

**Lines**: 54-58

```python
class ProgressContentSignature(dspy.Signature):
    task = dspy.InputField(desc="Task being performed")
    status_text = dspy.OutputField(desc="Current status message")
```

**Reusability**: HIGH - Generic progress indicator

---

### ActionContentSignature (dspy.Signature)

**Purpose**: Generate action button text and description

**Lines**: 61-66

```python
class ActionContentSignature(dspy.Signature):
    action_type = dspy.InputField(desc="Type of action (approve, delete, submit, etc.)")
    button_text = dspy.OutputField(desc="Button label")
    description = dspy.OutputField(desc="Action description")
```

**Reusability**: HIGH - Works for any action button

---

### ConfirmationContentSignature (dspy.Signature)

**Purpose**: Generate confirmation dialog content

**Lines**: 69-74

```python
class ConfirmationContentSignature(dspy.Signature):
    action = dspy.InputField(desc="Action to confirm")
    title = dspy.OutputField(desc="Dialog title")
    message = dspy.OutputField(desc="Confirmation message")
```

**Reusability**: HIGH - Generic confirmation pattern

---

### ImageContentSignature (dspy.Signature)

**Purpose**: Generate image widget content

**Lines**: 77-82

```python
class ImageContentSignature(dspy.Signature):
    subject = dspy.InputField(desc="Image subject or theme")
    title = dspy.OutputField(desc="Image title")
    caption = dspy.OutputField(desc="Image caption or description")
```

**Reusability**: HIGH - Works for any image widget

---

### GalleryContentSignature (dspy.Signature)

**Purpose**: Generate gallery widget content

**Lines**: 85-90

```python
class GalleryContentSignature(dspy.Signature):
    theme = dspy.InputField(desc="Gallery theme")
    title = dspy.OutputField(desc="Gallery title")
    description = dspy.OutputField(desc="Gallery description")
```

**Reusability**: HIGH - Good for galleries

---

### ChartContentSignature (dspy.Signature)

**Purpose**: Generate chart widget content

**Lines**: 93-98

```python
class ChartContentSignature(dspy.Signature):
    data_topic = dspy.InputField(desc="Chart data topic")
    title = dspy.OutputField(desc="Chart title")
    description = dspy.OutputField(desc="Chart description")
```

**Reusability**: HIGH - Generic chart signature

---

## File Summary

**Assessment**: Well-organized DSPy signatures with clear input/output contracts. Good coverage of widget types.

**Key Learnings**:
1. DSPy Signatures define I/O contracts clearly
2. Descriptive fields help LLM understanding
3. Generic signatures are more reusable
4. Too-specific signatures (WeatherCard) limit reuse

**Recommendations**:
- Consider consolidating similar signatures
- Add validation constraints to fields
- Document expected output formats
- Consider signature inheritance for related types

**Patterns Used**:
- DSPy Signature pattern
- Clear field descriptions guide LLM behavior
- Separation of concerns (one signature per widget type)

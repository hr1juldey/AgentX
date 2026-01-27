# Function Postmortem: api/generators/text_widgets.py

## Metadata
- **File**: prototypes/R014_ui_showcase/backend/api/generators/text_widgets.py
- **Lines of Code**: 79
- **Purpose**: Generate content for markdown, card, and form widgets
- **Dependencies**: dspy, api.dspy_signatures, api.models

---

## Analysis

**Status**: Working async widget generators for text-based components

**Purpose**: Contains static async methods that use DSPy to generate content for text widgets (markdown, cards, forms).

**Architecture**: Static method pattern - stateless generators

---

## Functions/Classes Extracted

### TextWidgetGenerator (class)

**Purpose**: Generate content for text-based widgets

**Pattern**: Static methods only - no instance state

---

### generate_markdown (staticmethod)

**Purpose**: Generate markdown content from topic

**Signature**: `async def generate_markdown(prompt: str) -> UIDescriptor`

**Lines**: 22-33

**Key Code**:
```python
@staticmethod
async def generate_markdown(prompt: str) -> UIDescriptor:
    generator = dspy.Predict(MarkdownContentSignature)
    result = generator(topic=prompt)
    return UIDescriptor(
        id=f"markdown-{datetime.now().timestamp()}",
        type="markdown",
        timestamp=datetime.now().isoformat(),
        content=result.content,
        metadata={"format": "markdown"},
    )
```

**What Works**:
- Simple and effective
- DSPy Predict usage is correct
- Timestamp-based ID generation

**Mistakes Found**:
- No validation of markdown format
- No length limits on content

**Behavioral Notes**:
- LLM generates full markdown content
- Format is always "markdown"
- No title field for markdown widgets

**Dependencies**:
- dspy.Predict
- MarkdownContentSignature
- UIDescriptor

**Reusability**: HIGH - Good generic markdown generator

---

### generate_card (staticmethod)

**Purpose**: Generate card with title, content, and actions

**Signature**: `async def generate_card(prompt: str) -> UIDescriptor`

**Lines**: 35-52

**Key Code**:
```python
@staticmethod
async def generate_card(prompt: str) -> UIDescriptor:
    generator = dspy.Predict(CardContentSignature)
    result = generator(topic=prompt)
    return UIDescriptor(
        id=f"card-{datetime.now().timestamp()}",
        type="card",
        timestamp=datetime.now().isoformat(),
        title=result.title,
        content=result.content,
        metadata={
            "icon": "sparkles",
            "actions": [
                {"label": "Learn More", "action": "more", "variant": "outline"}
            ],
        },
    )
```

**What Works**:
- LLM generates title and content
- Includes icon for visual appeal
- Has action button support

**Mistakes Found**:
- Icon is hardcoded to "sparkles"
- Action is always "Learn More" - not dynamic
- Only one action - could support multiple

**Behavioral Notes**:
- Icon never changes
- Action is static
- Good for showcase but not production

**Dependencies**:
- dspy.Predict
- CardContentSignature
- UIDescriptor

**Reusability**: MEDIUM - Good foundation, needs dynamic metadata

---

### generate_form (staticmethod)

**Purpose**: Generate form with title, description, and fields

**Signature**: `async def generate_form(prompt: str) -> UIDescriptor`

**Lines**: 54-78

**Key Code**:
```python
@staticmethod
async def generate_card(prompt: str) -> UIDescriptor:
    generator = dspy.Predict(FormContentSignature)
    result = generator(form_type=prompt)
    return UIDescriptor(
        id=f"form-{datetime.now().timestamp()}",
        type="form",
        timestamp=datetime.now().isoformat(),
        title=result.title,
        content=result.description,
        metadata={
            "form_id": "dynamic-form",
            "submit_label": "Submit",
            "fields": [
                {
                    "name": "response",
                    "type": "textarea",
                    "label": "Your Response",
                    "required": True,
                    "placeholder": "Type here...",
                }
            ],
        },
    )
```

**What Works**:
- LLM generates contextual title and description
- Good field structure
- Required field indicator

**Mistakes Found**:
- Fields are completely hardcoded
- LLM output (title/description) is used but fields are static
- Form ID never changes
- Always returns single textarea field

**Behavioral Notes**:
- Ignores form_type for field generation
- Could generate different fields based on type
- Very limited form structure

**Dependencies**:
- dspy.Predict
- FormContentSignature
- UIDescriptor

**Reusability**: LOW - Fields are too static

---

## File Summary

**Assessment**: Solid foundation with good DSPy usage, but too much hardcoding in metadata fields limits reusability.

**Key Learnings**:
1. DSPy Predict works well for content generation
2. Static metadata is convenient but limiting
3. LLM generates good titles and descriptions
4. Hardcoded fields/forms don't scale

**Mistakes to Avoid**:
1. Don't hardcode what should be dynamic (fields, actions)
2. Don't ignore LLM output for structuring data
3. Don't fix IDs that should be unique per instance

**Recommendations**:
1. Use LLM to generate field structures
2. Make icons and actions dynamic
3. Add parameters for metadata customization
4. Consider form-specific signatures for field generation

**Reusability Score**: MEDIUM - Good patterns, needs dynamic metadata

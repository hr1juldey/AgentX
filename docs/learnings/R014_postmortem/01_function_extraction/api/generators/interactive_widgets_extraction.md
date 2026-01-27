# Function Postmortem: api/generators/interactive_widgets.py

## Metadata
- **File**: prototypes/R014_ui_showcase/backend/api/generators/interactive_widgets.py
- **Lines of Code**: 77
- **Purpose**: Generate content for progress, action, and confirmation widgets
- **Dependencies**: dspy, api.dspy_signatures, api.models

---

## Analysis

**Status**: Working async widget generators for interactive UI components

**Purpose**: Contains static async methods that use DSPy to generate content for interactive widgets (progress bars, action buttons, confirmation dialogs).

**Architecture**: Static method pattern - stateless generators

---

## Functions/Classes Extracted

### InteractiveWidgetGenerator (class)

**Purpose**: Generate content for interactive widgets

**Pattern**: Static methods only - no instance state

---

### generate_progress (staticmethod)

**Purpose**: Generate progress widget with status text

**Signature**: `async def generate_progress(prompt: str) -> UIDescriptor`

**Lines**: 22-38

**Key Code**:
```python
@staticmethod
async def generate_progress(prompt: str) -> UIDescriptor:
    generator = dspy.Predict(ProgressContentSignature)
    result = generator(task=prompt)
    return UIDescriptor(
        id=f"progress-{datetime.now().timestamp()}",
        type="progress",
        timestamp=datetime.now().isoformat(),
        title="Processing",
        content=result.status_text,
        metadata={
            "value": 0.6,
            "indeterminate": False,
            "status_text": result.status_text,
        },
    )
```

**What Works**:
- DSPy Predict usage is correct
- Timestamp-based ID generation
- Hardcoded progress value (0.6) for demo

**Mistakes Found**:
- Progress value is hardcoded - should be dynamic
- Title is always "Processing" - not contextual

**Behavioral Notes**:
- Always returns 60% progress
- Determinate progress (not indeterminate)
- Timestamp-based IDs prevent collisions

**Dependencies**:
- dspy.Predict
- ProgressContentSignature
- UIDescriptor

**Reusability**: MEDIUM - Good pattern but needs parameterization

---

### generate_action (staticmethod)

**Purpose**: Generate action button with label and description

**Signature**: `async def generate_action(prompt: str) -> UIDescriptor`

**Lines**: 40-56

**Key Code**:
```python
@staticmethod
async def generate_action(prompt: str) -> UIDescriptor:
    generator = dspy.Predict(ActionContentSignature)
    result = generator(action_type=prompt)
    return UIDescriptor(
        id=f"action-{datetime.now().timestamp()}",
        type="action",
        timestamp=datetime.now().isoformat(),
        title=result.description,
        content="Click the button below",
        metadata={
            "button_text": result.button_text,
            "action_id": "action_click",
            "variant": "default",
        },
    )
```

**What Works**:
- LLM generates button text dynamically
- Generic content message
- Action ID for frontend handling

**Mistakes Found**:
- action_id is hardcoded - should be dynamic
- Content text is static - could be LLM-generated
- Variant is hardcoded

**Behavioral Notes**:
- Content text is always "Click the button below"
- Action ID doesn't change
- Variant always "default"

**Dependencies**:
- dspy.Predict
- ActionContentSignature
- UIDescriptor

**Reusability**: MEDIUM - Good foundation, needs parameterization

---

### generate_confirmation (staticmethod)

**Purpose**: Generate confirmation dialog with title and message

**Signature**: `async def generate_confirmation(prompt: str) -> UIDescriptor`

**Lines**: 58-76

**Key Code**:
```python
@staticmethod
async def generate_confirmation(prompt: str) -> UIDescriptor:
    generator = dspy.Predict(ConfirmationContentSignature)
    result = generator(action=prompt)
    return UIDescriptor(
        id=f"confirmation-{datetime.now().timestamp()}",
        type="confirmation",
        timestamp=datetime.now().isoformat(),
        title=result.title,
        content=result.message,
        metadata={
            "confirm_label": "Confirm",
            "cancel_label": "Cancel",
            "confirm_action": "confirm_yes",
            "cancel_action": "confirm_no",
            "variant": "default",
        },
    )
```

**What Works**:
- LLM generates contextual title and message
- Clear action IDs for frontend
- Both confirm and cancel actions defined

**Mistakes Found**:
- Labels are hardcoded - should be customizable
- Action IDs are hardcoded
- Variant is hardcoded

**Behavioral Notes**:
- Always uses "Confirm"/"Cancel" labels
- Action IDs never change
- Could support different confirmation styles

**Dependencies**:
- dspy.Predict
- ConfirmationContentSignature
- UIDescriptor

**Reusability**: MEDIUM - Good pattern, needs more flexibility

---

## File Summary

**Assessment**: Solid implementation of interactive widget generators using DSPy. Good patterns but too much hardcoding in metadata fields.

**Key Learnings**:
1. Static methods work well for stateless generators
2. DSPy Predict is straightforward for content generation
3. Timestamp-based IDs prevent collisions
4. Hardcoded metadata limits reusability

**Mistakes to Avoid**:
1. Don't hardcode values that should be dynamic
2. Don't use static text when LLM could generate it
3. Don't fix action IDs - make them configurable

**Recommendations**:
1. Add parameters for metadata customization
2. Consider LLM generation for static content fields
3. Add config object for default values
4. Make action IDs dynamic based on context

**Reusability Score**: MEDIUM - Good patterns but needs parameterization

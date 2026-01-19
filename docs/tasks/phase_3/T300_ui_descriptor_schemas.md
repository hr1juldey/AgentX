# T300: Create UI Descriptor Schemas

**Phase**: 3
**Estimated Time**: 40 minutes
**Dependencies**: T001
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/ui_descriptor_contract.md` - UI descriptor definitions
- `lld/incremental_release_plan.md` - Phase 3: All 7 core descriptors

**Description**:
Creates Pydantic schemas for all 7 core UI descriptors. These define the contract between agent and frontend for generative UI.

---

## Acceptance Criteria

**Passing Criteria**:
- ui/descriptors/ directory exists
- BaseUIDescriptor defined
- All 7 descriptor types defined (Markdown, Card, Form, Progress, Action, Confirmation, Voice)
- All descriptors inherit from BaseUIDescriptor
- All descriptors can be imported
- All descriptors validate with Pydantic

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify directory exists
test -d agentx/ui/descriptors && echo "descriptors directory exists"

# Verify descriptors can be imported
python3 -c "from agentx.ui.descriptors import MarkdownBlockDescriptor, CardDescriptor, FormDescriptor; print('Descriptors OK')"
```

---

## Implementation Steps

### Step 1: Create base descriptor and enums

Create file `agentx/ui/descriptors/base.py`:

```python
"""Base UI descriptor and enumerations."""

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class UIDescriptorType(str, Enum):
    """All supported UI descriptor types."""

    MARKDOWN_BLOCK = "markdown_block"
    CARD = "card"
    FORM = "form"
    PROGRESS = "progress"
    ACTION = "action"
    CONFIRMATION = "confirmation"
    VOICE = "voice"


class BaseUIDescriptor(BaseModel):
    """Base class for all UI descriptors.

    All UI components inherit from this base class.
    """

    descriptor_id: str = Field(..., description="Unique identifier for this UI element")
    descriptor_type: UIDescriptorType = Field(..., description="Type of UI element")
    display_name: Optional[str] = Field(None, description="Human-readable name")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extensible metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    dismissible: bool = Field(default=True, description="Whether user can dismiss this element")

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### Step 2: Create MarkdownBlock descriptor

Create file `agentx/ui/descriptors/markdown_block.py`:

```python
"""Markdown block descriptor."""

from pydantic import Field

from agentx.ui.descriptors.base import BaseUIDescriptor, UIDescriptorType


class MarkdownBlockDescriptor(BaseUIDescriptor):
    """Descriptor for rendering markdown text blocks.

    Used for displaying rich text content with markdown formatting.
    """

    descriptor_type: UIDescriptorType = UIDescriptorType.MARKDOWN_BLOCK
    content: str = Field(..., description="Markdown content to render")
    allow_copy: bool = Field(default=True, description="Allow copying content")
    max_height: Optional[str] = Field(None, description="CSS max-height (e.g., '300px')")
```

### Step 3: Create Card descriptor

Create file `agentx/ui/descriptors/card.py`:

```python
"""Card descriptor."""

from typing import List, Optional
from pydantic import Field

from agentx.ui.descriptors.base import BaseUIDescriptor, UIDescriptorType


class CardAction(BaseModel):
    """Action button for card."""

    action_id: str = Field(..., description="Unique action identifier")
    label: str = Field(..., description="Button label text")
    variant: str = Field(default="primary", description="Visual style (primary, secondary, danger)")
    icon: Optional[str] = Field(None, description="Icon name")


class CardDescriptor(BaseUIDescriptor):
    """Descriptor for card widgets.

    Cards display structured content with title, body, and optional actions.
    """

    descriptor_type: UIDescriptorType = UIDescriptorType.CARD
    title: str = Field(..., description="Card title")
    content: str = Field(..., description="Card content (markdown supported)")
    actions: List[CardAction] = Field(default_factory=list, description="Action buttons")
    variant: str = Field(default="default", description="Visual variant (default, outlined, elevated)")
    image_url: Optional[str] = Field(None, description="Optional image URL")
```

### Step 4: Create Form descriptor

Create file `agentx/ui/descriptors/form.py`:

```python
"""Form descriptor."""

from typing import List, Optional
from pydantic import Field, BaseModel

from agentx.ui.descriptors.base import BaseUIDescriptor, UIDescriptorType


class FormFieldType(str):
    """Form field types."""

    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    EMAIL = "email"
    PASSWORD = "password"
    SELECT = "select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    DATE = "date"
    TIME = "time"


class FormField(BaseModel):
    """Single form field definition."""

    field_name: str = Field(..., description="Unique field identifier")
    field_type: str = Field(..., description="Type of input field")
    label: str = Field(..., description="Human-readable label")
    placeholder: Optional[str] = Field(None, description="Placeholder text")
    required: bool = Field(default=False, description="Whether field is required")
    default_value: Optional[str] = Field(None, description="Default value")
    options: Optional[List[str]] = Field(None, description="Options for select/radio")
    validation_regex: Optional[str] = Field(None, description="Validation pattern")


class FormDescriptor(BaseUIDescriptor):
    """Descriptor for user input forms.

    Forms collect structured input from users.
    """

    descriptor_type: UIDescriptorType = UIDescriptorType.FORM
    form_id: str = Field(..., description="Unique form identifier")
    title: Optional[str] = Field(None, description="Form title")
    description: Optional[str] = Field(None, description="Form description")
    fields: List[FormField] = Field(..., description="Form fields")
    submit_button_text: str = Field(default="Submit", description="Submit button text")
    cancel_button_text: Optional[str] = Field(None, description="Cancel button text (shows cancel if set)")
    interrupt_agent: bool = Field(default=True, description="Pause agent while form is open")
    timeout_seconds: int = Field(default=300, description="Form auto-submit timeout")
```

### Step 5: Create Progress descriptor

Create file `agentx/ui/descriptors/progress.py`:

```python
"""Progress indicator descriptor."""

from pydantic import Field

from agentx.ui.descriptors.base import BaseUIDescriptor, UIDescriptorType


class ProgressDescriptor(BaseUIDescriptor):
    """Descriptor for progress indicators.

    Shows progress for long-running operations.
    """

    descriptor_type: UIDescriptorType = UIDescriptorType.PROGRESS
    task_name: str = Field(..., description="Task name being performed")
    progress_percent: int = Field(..., ge=0, le=100, description="Progress percentage (0-100)")
    status_text: Optional[str] = Field(None, description="Current status text")
    indeterminate: bool = Field(default=False, description="Show indeterminate progress (spinner)")
    striped: bool = Field(default=True, description="Show striped animation")
    show_percentage: bool = Field(default=True, description="Display percentage text")
```

### Step 6: Create Action descriptor

Create file `agentx/ui/descriptors/action.py`:

```python
"""Action button descriptor."""

from pydantic import Field

from agentx.ui.descriptors.base import BaseUIDescriptor, UIDescriptorType


class ActionDescriptor(BaseUIDescriptor):
    """Descriptor for standalone action buttons.

    Simple button to trigger an action.
    """

    descriptor_type: UIDescriptorType = UIDescriptorType.ACTION
    button_text: str = Field(..., description="Button label text")
    action_id: str = Field(..., description="Action identifier")
    variant: str = Field(default="primary", description="Visual style")
    icon: Optional[str] = Field(None, description="Icon name")
    disabled: bool = Field(default=False, description="Whether button is disabled")
    confirm: bool = Field(default=False, description="Require confirmation before action")
```

### Step 7: Create Confirmation descriptor

Create file `agentx/ui/descriptors/confirmation.py`:

```python
"""Confirmation dialog descriptor."""

from pydantic import Field

from agentx.ui.descriptors.base import BaseUIDescriptor, UIDescriptorType


class ConfirmationDescriptor(BaseUIDescriptor):
    """Descriptor for confirmation dialogs.

    Requires user confirmation before proceeding.
    """

    descriptor_type: UIDescriptorType = UIDescriptorType.CONFIRMATION
    title: str = Field(..., description="Dialog title")
    message: str = Field(..., description="Confirmation message")
    confirm_text: str = Field(default="Confirm", description="Confirm button text")
    cancel_text: str = Field(default="Cancel", description="Cancel button text")
    risk_level: str = Field(default="medium", description="Risk level (low, medium, high)")
    dangerous: bool = Field(default=False, description="Is this a dangerous action")
```

### Step 8: Create Voice descriptor

Create file `agentx/ui/descriptors/voice.py`:

```python
"""Voice input descriptor."""

from pydantic import Field

from agentx.ui.descriptors.base import BaseUIDescriptor, UIDescriptorType


class VoiceDescriptor(BaseUIDescriptor):
    """Descriptor for voice input.

    Records audio from user microphone.
    """

    descriptor_type: UIDescriptorType = UIDescriptorType.VOICE
    max_duration_seconds: int = Field(default=60, description="Maximum recording duration")
    auto_submit: bool = Field(default=False, description="Auto-submit after recording")
    show_waveform: bool = Field(default=True, description="Show audio waveform visualization")
    prompt_text: Optional[str] = Field(None, description="Prompt text for user")
```

### Step 9: Create descriptors __init__.py

Create file `agentx/ui/descriptors/__init__.py`:

```python
"""UI descriptor schemas for AGENTX."""

from agentx.ui.descriptors.base import (
    BaseUIDescriptor,
    UIDescriptorType,
)
from agentx.ui.descriptors.markdown_block import MarkdownBlockDescriptor
from agentx.ui.descriptors.card import CardDescriptor, CardAction
from agentx.ui.descriptors.form import FormDescriptor, FormField, FormFieldType
from agentx.ui.descriptors.progress import ProgressDescriptor
from agentx.ui.descriptors.action import ActionDescriptor
from agentx.ui.descriptors.confirmation import ConfirmationDescriptor
from agentx.ui.descriptors.voice import VoiceDescriptor

__all__ = [
    "BaseUIDescriptor",
    "UIDescriptorType",
    "MarkdownBlockDescriptor",
    "CardDescriptor",
    "CardAction",
    "FormDescriptor",
    "FormField",
    "FormFieldType",
    "ProgressDescriptor",
    "ActionDescriptor",
    "ConfirmationDescriptor",
    "VoiceDescriptor",
]
```

---

## Expected Failures & Countermeasures

### Failure: Pydantic validation error

**Likelihood**: Low
**Symptoms**: `pydantic.ValidationError` on descriptor creation

**Countermeasures**:
1. Check all required fields have values
2. Ensure field types match (str, int, bool, etc.)
3. Verify enum values are valid
4. Check ge/le constraints (e.g., progress_percent 0-100)

**Recovery Time**: 5 minutes

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T001 directory structure changed
**Detection**: agentx/ui/descriptors/ directory missing
**Action**: Re-run T001 to ensure all directories exist

**Recovery Time**: 5 minutes

### Downstream Impact

**Scenario**: Descriptor field names change
**Prevention**: All descriptor field names are LOCKED
**Mitigation**: Update UI agent, frontend, and WebSocket serialization
**Affected Tasks**: T302 (UI DSPy Agent), T303 (WebSocket), Phase 6 (Frontend)

---

## Artifacts

**Files Created**:
- `agentx/ui/descriptors/base.py` (Base descriptor, LOCKED)
- `agentx/ui/descriptors/markdown_block.py` (Markdown, LOCKED)
- `agentx/ui/descriptors/card.py` (Card, LOCKED)
- `agentx/ui/descriptors/form.py` (Form, LOCKED)
- `agentx/ui/descriptors/progress.py` (Progress, LOCKED)
- `agentx/ui/descriptors/action.py` (Action, LOCKED)
- `agentx/ui/descriptors/confirmation.py` (Confirmation, LOCKED)
- `agentx/ui/descriptors/voice.py` (Voice, LOCKED)
- `agentx/ui/descriptors/__init__.py` (Package marker)

**Locked APIs**:
- All descriptor class names
- All descriptor field names and types
- UIDescriptorType enum values

---

## Quality Gates

**Quality Checks**:
- **Check**: All descriptor files exist
  - Command: `ls agentx/ui/descriptors/*.py`
  - Expected: 9 .py files
  - Required: Yes

- **Check**: Descriptors can be imported
  - Command: `python3 -c "from agentx.ui.descriptors import MarkdownBlockDescriptor, CardDescriptor, FormDescriptor; print('OK')"`
  - Expected: `OK`
  - Required: Yes

- **Check**: Descriptors validate correctly
  - Command: `python3 -c "from agentx.ui.descriptors import MarkdownBlockDescriptor; d = MarkdownBlockDescriptor(descriptor_id='test', content='Hello'); print(d.descriptor_type)"` 2>&1
  - Expected: `markdown_block`
  - Required: Yes

---

## Notes

1. All descriptors inherit from BaseUIDescriptor
2. descriptor_id unique per component
3. descriptor_type enum determines renderer
4. dismissible controls UI behavior
5. Form can interrupt agent execution
6. Progress supports indeterminate mode
7. Voice has max duration limit
8. All descriptors validate with Pydantic

---

## Completion Checklist

- [ ] base.py created with BaseUIDescriptor
- [ ] markdown_block.py created
- [ ] card.py created with CardAction
- [ ] form.py created with FormField
- [ ] progress.py created
- [ ] action.py created
- [ ] confirmation.py created
- [ ] voice.py created
- [ ] __init__.py exports all descriptors
- [ ] All descriptors can be imported
- [ ] All descriptors validate with Pydantic
- [ ] Ready for T301 (UI DSPy Signatures)

---

**Task T300 is part of Phase 3: UI DSPy Agent + Descriptors**
**Locked APIs**: All descriptor class names, field names, and types

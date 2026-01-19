# AGENTX UI Descriptor Contract LLD

**Version**: 1.0.0
**Date**: 2026-01-19
**Status**: Locked
**Dependencies**: domain_model.md

---

## Table of Contents

1. [Descriptor Type System](#1-descriptor-type-system)
2. [Core Descriptors](#2-core-descriptors)
3. [WebSocket Messages](#3-websocket-messages)
4. [Lifecycle Rules](#4-lifecycle-rules)
5. [Validation Rules](#5-validation-rules)

---

## 1. Descriptor Type System

### 1.1 Descriptor Type Enum

**File**: `ui/descriptors/base.py`

```python
from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime


class UIDescriptorType(str, Enum):
    """Closed set of core UI descriptor types.

    Extensions via plugins must follow protocol.
    """

    MARKDOWN_BLOCK = "markdown_block"
    CARD = "card"
    FORM = "form"
    PROGRESS = "progress"
    ACTION = "action"
    CONFIRMATION = "confirmation"
    VOICE = "voice"


class BaseUIDescriptor(BaseModel):
    """Base class for all UI descriptors.

    All UI components must inherit from this.
    """

    descriptor_id: str = Field(..., description="Unique identifier for this UI element")
    descriptor_type: UIDescriptorType = Field(..., description="Type of UI element")
    display_name: Optional[str] = Field(None, description="Human-readable name")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extensible metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    dismissible: bool = Field(default=True, description="Whether user can dismiss")

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

---

## 2. Core Descriptors

### 2.1 MarkdownBlockDescriptor

**File**: `ui/descriptors/markdown_block.py`

```python
from pydantic import Field
from typing import Optional

from ui.descriptors.base import BaseUIDescriptor, UIDescriptorType


class MarkdownBlockDescriptor(BaseUIDescriptor):
    """Render markdown text content.

    Use case: Informational text, explanations, documentation.
    Lifecycle: Auto-dismiss after timeout (default: none, manual only).
    """

    descriptor_type: UIDescriptorType = UIDescriptorType.MARKDOWN_BLOCK
    content: str = Field(..., description="Markdown content to render")
    allow_copy: bool = Field(default=True, description="Allow copying content")
    max_height: Optional[str] = Field(None, description="CSS max-height (e.g., '300px')")
    overflow_y: str = Field(default="auto", description="CSS overflow-y behavior")
```

### 2.2 CardDescriptor

**File**: `ui/descriptors/card.py`

```python
from pydantic import Field
from typing import List, Optional

from ui.descriptors.base import BaseUIDescriptor, UIDescriptorType


class CardAction(BaseModel):
    """Action button on a card."""

    label: str = Field(..., description="Button label")
    action_id: str = Field(..., description="Action identifier")
    variant: str = Field(default="primary", description="Visual variant (primary/secondary/danger)")
    icon: Optional[str] = Field(None, description="Icon name")


class CardDescriptor(BaseUIDescriptor):
    """Display content in a card with optional actions.

    Use case: Information display with actions, notifications.
    Lifecycle: Manual dismiss or auto-replace on new content.
    """

    descriptor_type: UIDescriptorType = UIDescriptorType.CARD
    title: str = Field(..., description="Card title")
    content: str = Field(..., description="Card content (markdown supported)")
    actions: List[CardAction] = Field(default_factory=list, description="Action buttons")
    variant: str = Field(default="default", description="Visual variant (default/success/warning/danger)")
    size: str = Field(default="medium", description="Card size (small/medium/large)")
    dismissible: bool = Field(default=True, description="Show dismiss button")
```

### 2.3 FormDescriptor

**File**: `ui/descriptors/form.py`

```python
from pydantic import Field
from typing import List, Optional, Any, Dict
from enum import Enum

from ui.descriptors.base import BaseUIDescriptor, UIDescriptorType


class FormFieldType(str, Enum):
    """Form field types."""

    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    EMAIL = "email"
    PASSWORD = "password"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    DATE = "date"
    TIME = "time"
    FILE = "file"


class FormFieldOption(BaseModel):
    """Option for select/radio fields."""

    label: str = Field(..., description="Option label")
    value: Any = Field(..., description="Option value")


class FormField(BaseModel):
    """Single form field."""

    name: str = Field(..., description="Field name (key in form data)")
    label: str = Field(..., description="Field label")
    field_type: FormFieldType = Field(..., description="Type of field")
    placeholder: Optional[str] = Field(None, description="Placeholder text")
    default_value: Optional[Any] = Field(None, description="Default value")
    required: bool = Field(default=False, description="Field is required")
    options: List[FormFieldOption] = Field(default_factory=list, description="Options for select/radio")
    min_value: Optional[float] = Field(None, description="Minimum value (number fields)")
    max_value: Optional[float] = Field(None, description="Maximum value (number fields)")
    min_length: Optional[int] = Field(None, description="Minimum length (text fields)")
    max_length: Optional[int] = Field(None, description="Maximum length (text fields)")
    validation_regex: Optional[str] = Field(None, description="Validation regex pattern")
    help_text: Optional[str] = Field(None, description="Help text below field")


class FormDescriptor(BaseUIDescriptor):
    """Collect user input via multi-field form.

    Use case: User data collection, confirmations, multi-step input.
    Lifecycle: Interrupts agent until submitted or timeout.
    """

    descriptor_type: UIDescriptorType = UIDescriptorType.FORM
    form_id: str = Field(..., description="Unique form identifier")
    fields: List[FormField] = Field(..., description="Form fields")
    submit_button_text: str = Field(default="Submit", description="Submit button text")
    cancel_button_text: Optional[str] = Field(None, description="Cancel button text")
    interrupt_agent: bool = Field(default=True, description="Pause agent while form is open")
    timeout_seconds: int = Field(default=300, description="Auto-submit after timeout (0 = no timeout)")
    submit_on_enter: bool = Field(default=False, description="Submit on Enter key (single-field forms)")
    dismissible: bool = Field(default=True, description="Allow cancel/dismiss")
```

### 2.4 ProgressDescriptor

**File**: `ui/descriptors/progress.py`

```python
from pydantic import Field

from ui.descriptors.base import BaseUIDescriptor, UIDescriptorType


class ProgressDescriptor(BaseUIDescriptor):
    """Show progress for long-running tasks.

    Use case: File uploads, batch processing, multi-step operations.
    Lifecycle: Auto-dismiss when complete or dismissible manual.
    """

    descriptor_type: UIDescriptorType = UIDescriptorType.PROGRESS
    task_name: str = Field(..., description="Name of the task")
    progress_percent: int = Field(..., ge=0, le=100, description="Progress percentage (0-100)")
    status_text: str = Field(default="", description="Current status text")
    indeterminate: bool = Field(default=False, description="Indeterminate progress (spinner)")
    striped: bool = Field(default=True, description="Show striped animation")
    show_percentage: bool = Field(default=True, description="Show percentage text")
    color: str = Field(default="primary", description="Progress bar color")
    dismiss_on_complete: bool = Field(default=True, description="Auto-dismiss when 100%")
```

### 2.5 ActionDescriptor

**File**: `ui/descriptors/action.py`

```python
from pydantic import Field
from typing import Optional

from ui.descriptors.base import BaseUIDescriptor, UIDescriptorType


class ActionDescriptor(BaseUIDescriptor):
    """Display standalone action button.

    Use case: Quick actions, confirmations, triggers.
    Lifecycle: Dismiss on click or manual.
    """

    descriptor_type: UIDescriptorType = UIDescriptorType.ACTION
    button_text: str = Field(..., description="Button text")
    action_id: str = Field(..., description="Action identifier")
    variant: str = Field(default="primary", description="Visual variant (primary/secondary/danger)")
    size: str = Field(default="medium", description="Button size (small/medium/large)")
    icon: Optional[str] = Field(None, description="Icon name")
    disabled: bool = Field(default=False, description="Disable button")
    loading: bool = Field(default=False, description="Show loading spinner")
    dismissible: bool = Field(default=True, description="Allow dismiss without action")
```

### 2.6 ConfirmationDescriptor

**File**: `ui/descriptors/confirmation.py`

```python
from pydantic import Field
from typing import Optional, List

from ui.descriptors.base import BaseUIDescriptor, UIDescriptorType


class ConfirmationDescriptor(BaseUIDescriptor):
    """Request user confirmation for an action.

    Use case: Destructive actions, irreversible operations.
    Lifecycle: Interrupts agent until confirmed or cancelled.
    """

    descriptor_type: UIDescriptorType = UIDescriptorType.CONFIRMATION
    title: str = Field(..., description="Dialog title")
    message: str = Field(..., description="Confirmation message (markdown)")
    confirm_text: str = Field(default="Confirm", description="Confirm button text")
    cancel_text: str = Field(default="Cancel", description="Cancel button text")
    risk_level: str = Field(default="medium", description="Risk level (low/medium/high/critical)")
    show_danger_icon: bool = Field(default=True, description="Show warning icon")
    require_typing: bool = Field(default=False, description="Require typing confirmation for critical")
    typing_confirmation: Optional[str] = Field(None, description="Text user must type to confirm")
    dismissible: bool = Field(default=True, description="Allow dismiss (cancel)")
```

### 2.7 VoiceDescriptor

**File**: `ui/descriptors/voice.py`

```python
from pydantic import Field
from typing import Optional

from ui.descriptors.base import BaseUIDescriptor, UIDescriptorType


class VoiceDescriptor(BaseUIDescriptor):
    """Record voice input from user.

    Use case: Voice commands, dictation, voice queries.
    Lifecycle: Auto-dismiss after recording or manual.
    """

    descriptor_type: UIDescriptorType = UIDescriptorType.VOICE
    max_duration_seconds: int = Field(default=60, description="Maximum recording duration")
    auto_submit: bool = Field(default=False, description="Auto-submit after recording")
    show_waveform: bool = Field(default=True, description="Show audio waveform")
    show_timer: bool = Field(default=True, description="Show recording timer")
    silence_threshold_ms: int = Field(default=1000, description="Silence threshold (ms)")
    prompt_text: Optional[str] = Field(None, description="Prompt text to show")
    dismissible: bool = Field(default=True, description="Allow cancel")
```

---

## 3. WebSocket Messages

### 3.1 Message Types

**File**: `ui/protocols/websocket_messages.py`

```python
from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime


class WebSocketMessageType(str, Enum):
    """WebSocket message types.

    Organized by category.
    """

    # Agent messages
    TOKEN = "token"
    REASONING_STEP = "reasoning_step"
    TOOL_CALL = "tool_call"
    STATUS_UPDATE = "status_update"

    # UI messages
    DESCRIPTOR_CREATE = "descriptor_create"
    DESCRIPTOR_UPDATE = "descriptor_update"
    DESCRIPTOR_DISMISS = "descriptor_dismiss"

    # System messages
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

    # Session messages
    SESSION_PAUSE = "session_pause"
    SESSION_RESUME = "session_resume"
    SESSION_CLOSE = "session_close"

    # Form messages
    FORM_SHOW = "form_show"
    FORM_SUBMIT = "form_submit"
    FORM_VALIDATE = "form_validate"

    # Progress messages
    PROGRESS_START = "progress_start"
    PROGRESS_UPDATE = "progress_update"
    PROGRESS_COMPLETE = "progress_complete"


class WebSocketMessage(BaseModel):
    """Base WebSocket message structure."""

    message_type: WebSocketMessageType = Field(..., description="Message type")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: str = Field(..., description="Session identifier")
    data: Dict[str, Any] = Field(default_factory=dict, description="Message payload")
    message_id: Optional[str] = Field(None, description="Unique message identifier (for deduplication)")
    correlation_id: Optional[str] = Field(None, description="Correlation ID (for request/response)")


# Agent Message Payloads

class TokenPayload(BaseModel):
    """Token streaming payload."""

    token: str = Field(..., description="Text token")
    is_first: bool = Field(default=False, description="First token in stream")
    is_last: bool = Field(default=False, description="Last token in stream")


class ReasoningStepPayload(BaseModel):
    """Reasoning step payload."""

    step_number: int = Field(..., description="Step number")
    thought: str = Field(..., description="Agent thought")
    action: Optional[str] = Field(None, description="Action taken")
    observation: Optional[str] = Field(None, description="Action result")


class ToolCallPayload(BaseModel):
    """Tool call payload."""

    tool_name: str = Field(..., description="Tool name")
    arguments: Dict[str, Any] = Field(..., description="Tool arguments")
    status: str = Field(..., description="Status (executing/completed/error)")
    result: Optional[str] = Field(None, description="Tool result")
    error: Optional[str] = Field(None, description="Error message")


# UI Message Payloads

class DescriptorCreatePayload(BaseModel):
    """UI descriptor creation payload."""

    descriptor: Dict[str, Any] = Field(..., description="Full descriptor data")
    position: Optional[str] = Field(None, description="Position (append/replace/modal)")


class DescriptorUpdatePayload(BaseModel):
    """UI descriptor update payload."""

    component_id: str = Field(..., description="Component ID")
    updates: Dict[str, Any] = Field(..., description="Fields to update")


class DescriptorDismissPayload(BaseModel):
    """UI descriptor dismiss payload."""

    component_id: str = Field(..., description="Component ID")
    reason: Optional[str] = Field(None, description="Dismiss reason")


# Form Message Payloads

class FormShowPayload(BaseModel):
    """Show form payload."""

    form_id: str = Field(..., description="Form ID")
    descriptor: Dict[str, Any] = Field(..., description="Form descriptor")


class FormSubmitPayload(BaseModel):
    """Submit form payload."""

    form_id: str = Field(..., description="Form ID")
    form_data: Dict[str, Any] = Field(..., description="Form data")
    submit_action: Optional[str] = Field(None, description="Submit action")


# Progress Message Payloads

class ProgressUpdatePayload(BaseModel):
    """Progress update payload."""

    task_id: str = Field(..., description="Task ID")
    progress_percent: int = Field(..., ge=0, le=100)
    status_text: str = Field(..., description="Status text")
    indeterminate: bool = Field(default=False)
```

### 3.2 Message Flows

#### Token Streaming Flow

```
Server → Client: TOKEN (TokenPayload)
  - message_type: "token"
  - data.token: "Hello"
  - data.is_first: true
  - correlation_id: "query_123"

Server → Client: TOKEN (TokenPayload)
  - data.token: " world"
  - data.is_last: true
  - correlation_id: "query_123"
```

#### UI Descriptor Flow

```
Server → Client: DESCRIPTOR_CREATE (DescriptorCreatePayload)
  - data.descriptor: {CardDescriptor}
  - data.position: "append"

User clicks card action

Client → Server: FORM_SUBMIT (FormSubmitPayload)
  - data.form_id: "form_123"
  - data.form_data: {field: value}

Server → Client: DESCRIPTOR_DISMISS (DescriptorDismissPayload)
  - data.component_id: "form_123"
```

---

## 4. Lifecycle Rules

### 4.1 State Machine

```
CREATING → CREATED → UPDATING → DISMISSED
            ↓
        (visible)
```

### 4.2 Type-Specific Rules

| Descriptor Type | Dismissible | Timeout | Auto-Replace | Interrupt |
|-----------------|------------|---------|--------------|-----------|
| MARKDOWN_BLOCK | ✅ | Optional | No | No |
| CARD | ✅ | Optional | Yes | No |
| FORM | ✅ (cancel) | Yes (300s) | No | Yes |
| PROGRESS | ✅ | On complete | Yes | No |
| ACTION | ✅ | None | No | No |
| CONFIRMATION | ✅ (cancel) | None | No | Yes |
| VOICE | ✅ | Max duration | Yes | No |

### 4.3 Replacement Rules

**Priority Queue** (highest to lowest):
1. CONFIRMATION (interrupts everything)
2. FORM (interrupts, replaces existing form)
3. PROGRESS (shows alongside)
4. CARD (replaces existing card)
5. MARKDOWN_BLOCK (replaces existing markdown)
6. ACTION (shows alongside)

**Max Visible per Type**:
- MARKDOWN_BLOCK: 1
- CARD: 1
- FORM: 1 (only one active form)
- PROGRESS: 3 (stack multiple progress bars)
- ACTION: 5 (show up to 5 action buttons)
- CONFIRMATION: 1 (modal, blocks everything)
- VOICE: 1 (only one recording)

---

## 5. Validation Rules

### 5.1 Descriptor Validation

```python
def validate_descriptor(descriptor: Dict[str, Any]) -> bool:
    """Validate descriptor structure."""
    # Must have descriptor_type
    if "descriptor_type" not in descriptor:
        return False

    # Must have descriptor_id
    if "descriptor_id" not in descriptor:
        return False

    # Validate type-specific fields
    descriptor_type = descriptor["descriptor_type"]

    if descriptor_type == "form":
        # Form must have fields
        if "fields" not in descriptor or not descriptor["fields"]:
            return False

    elif descriptor_type == "progress":
        # Progress must have valid percentage
        if "progress_percent" in descriptor:
            pct = descriptor["progress_percent"]
            if not isinstance(pct, int) or not (0 <= pct <= 100):
                return False

    return True
```

### 5.2 Form Field Validation

```python
def validate_form_field(field: FormField, value: Any) -> tuple[bool, Optional[str]]:
    """Validate single form field value."""

    # Required check
    if field.required and (value is None or value == ""):
        return False, f"{field.label} is required"

    # Type-specific validation
    if field.field_type == FormFieldType.EMAIL and value:
        import re
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            return False, f"{field.label} must be a valid email"

    if field.field_type == FormFieldType.NUMBER and value:
        try:
            num = float(value)
            if field.min_value is not None and num < field.min_value:
                return False, f"{field.label} must be at least {field.min_value}"
            if field.max_value is not None and num > field.max_value:
                return False, f"{field.label} must be at most {field.max_value}"
        except (ValueError, TypeError):
            return False, f"{field.label} must be a number"

    if field.validation_regex and value:
        import re
        if not re.match(field.validation_regex, str(value)):
            return False, f"{field.label} format is invalid"

    # Length validation
    if field.min_length and len(str(value)) < field.min_length:
        return False, f"{field.label} must be at least {field.min_length} characters"

    if field.max_length and len(str(value)) > field.max_length:
        return False, f"{field.label} must be at most {field.max_length} characters"

    return True, None
```

---

**This UI descriptor contract is part of AGENTX LLD v1.0. All names and types are locked.**

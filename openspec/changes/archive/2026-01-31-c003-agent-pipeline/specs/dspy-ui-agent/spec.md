# Spec: dspy-ui-agent

**File**: `specs/dspy-ui-agent/spec.md`

**Generated**: 2026-01-28
**Change**: c003-agent-pipeline

---

## 1.1 Purpose

Define the UI specialist agent that generates UI descriptors for displaying content to users. The UIDSPyAgent is responsible for selecting appropriate widgets, configuring forms, generating cards and confirmations, and updating progress indicators.

---

## 1.2 Scope

**In Scope**:
- UIDSPyAgent class with 6 UI-specific signatures
- Widget selection logic (markdown_block, card, form, progress, action, confirmation, voice)
- Form schema generation and validation
- Integration with UI descriptor contracts from C002
- Tool-based UI generation returning descriptor IDs

**Out of Scope**:
- Frontend rendering of descriptors (frontend concern)
- WebSocket message formatting (covered by C002 data contracts)
- Main agent orchestration (covered by dspy-main-agent spec)

---

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-UI-001 | Agent MUST select widget type based on content_type and context | Must |
| FR-UI-002 | Agent MUST generate form schemas with field definitions | Must |
| FR-UI-003 | Agent MUST generate card descriptors with title, content, and actions | Must |
| FR-UI-004 | Agent MUST request confirmation with risk level assessment | Must |
| FR-UI-005 | Agent MUST update progress indicators with current/total steps | Must |
| FR-UI-006 | Agent MUST return descriptor IDs (not full descriptor objects) | Must |
| FR-UI-007 | Agent MUST NOT generate HTML or CSS directly | Must |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-UI-001 | Agent file MUST NOT exceed 80 lines | Must |
| NFR-UI-002 | Agent MUST use absolute imports only | Must |
| NFR-UI-003 | Agent MUST pass ruff check and ruff format | Must |

---

## 1.4 Data Model

**Locked from LLD: agent_runtime.md:486-580**

```python
# File: agent/dspy_agents/ui_agent.py
import dspy
from typing import Dict, Any, List

from agent.dspy_signatures.ui_signatures import (
    SelectWidgetSignature,
    ConfigureFormSignature,
    ShowCardSignature,
    RequestConfirmationSignature,
    UpdateProgressSignature
)


class UIDSPyAgent(dspy.Module):
    """UI specialist agent for generating UI descriptors.

    Responsible for:
    - Selecting appropriate widgets
    - Configuring forms
    - Generating cards and confirmations
    - Updating progress indicators
    """

    def __init__(self):
        super().__init__()

        self.widget_selector = dspy.Predict(SelectWidgetSignature)
        self.form_configurer = dspy.Predict(ConfigureFormSignature)
        self.card_generator = dspy.Predict(ShowCardSignature)
        self.confirmation_requester = dspy.Predict(RequestConfirmationSignature)
        self.progress_updater = dspy.Predict(UpdateProgressSignature)

    def select_widget(
        self,
        content_type: str,
        context: str
    ) -> dspy.Prediction:
        """Select appropriate UI widget."""

    def configure_form(
        self,
        required_fields: List[str],
        context: str
    ) -> dspy.Prediction:
        """Configure form schema."""

    def show_card(
        self,
        title: str,
        content: str,
        context: str
    ) -> dspy.Prediction:
        """Generate card widget."""

    def request_confirmation(
        self,
        action_description: str,
        risk_level: str
    ) -> dspy.Prediction:
        """Request user confirmation."""

    def update_progress(
        self,
        task_name: str,
        current_step: int,
        total_steps: int
    ) -> dspy.Prediction:
        """Update progress indicator."""
```

**Locked from LLD: agent_runtime.md:58-109**

```python
# File: agent/dspy_signatures/ui_signatures.py
import dspy
from typing import List, Dict, Any


class SelectWidgetSignature(dspy.Signature):
    """Select the appropriate UI widget for displaying content."""

    content_type: str = dspy.InputField(desc="Type of content (text, data, action, etc.)")
    context: str = dspy.InputField(desc="Additional context for widget selection")
    widget_type: str = dspy.OutputField(desc="Selected widget type")
    widget_config: Dict[str, Any] = dspy.OutputField(desc="Widget configuration")


class ConfigureFormSignature(dspy.Signature):
    """Configure a form schema for user input."""

    required_fields: List[str] = dspy.InputField(desc="Fields required from user")
    context: str = dspy.InputField(desc="Context for form configuration")
    form_schema: Dict[str, Any] = dspy.OutputField(desc="Form schema definition")


class ShowCardSignature(dspy.Signature):
    """Generate a card widget with title and content."""

    title: str = dspy.InputField(desc="Card title")
    content: str = dspy.InputField(desc="Card content (markdown supported)")
    context: str = dspy.InputField(desc="Additional context")
    show_actions: bool = dspy.OutputField(desc="Whether to show action buttons")
    card_descriptor: Dict[str, Any] = dspy.OutputField(desc="Card widget descriptor")


class RequestConfirmationSignature(dspy.Signature):
    """Request user confirmation for an action."""

    action_description: str = dspy.InputField(desc="Description of action to confirm")
    risk_level: str = dspy.InputField(desc="Risk level: low, medium, high")
    confirmation_dialog: Dict[str, Any] = dspy.OutputField(desc="Confirmation dialog descriptor")


class UpdateProgressSignature(dspy.Signature):
    """Update a progress indicator."""

    task_name: str = dspy.InputField(desc="Name of the task")
    current_step: int = dspy.InputField(desc="Current step number")
    total_steps: int = dspy.InputField(desc="Total number of steps")
    progress_descriptor: Dict[str, Any] = dspy.OutputField(desc="Progress widget descriptor")
```

**UI Tools from LLD: agent_runtime.md:260-346**

```python
# File: agent/tools/ui_tools.py
import dspy
from typing import Dict, Any, List
from datetime import datetime, timedelta
from uuid import UUID, uuid4


def render_markdown_block(text: str) -> str:
    """Render a markdown text block in the UI.

    Returns: UI descriptor ID
    """
    from ui.descriptors.markdown_block import MarkdownBlockDescriptor

    descriptor = MarkdownBlockDescriptor(
        descriptor_id=str(uuid4()),
        content=text,
        allow_copy=True,
    )

    # Store in UI component registry
    return f"MARKDOWN_BLOCK:{descriptor.descriptor_id}"


def render_card(title: str, content: str, actions: List[str]) -> str:
    """Render a card widget with title, content, and action buttons.

    Returns: UI descriptor ID
    """
    from ui.descriptors.card import CardDescriptor, CardAction

    card_actions = [
        CardAction(label=action, action_id=f"action_{i}")
        for i, action in enumerate(actions)
    ]

    descriptor = CardDescriptor(
        descriptor_id=str(uuid4()),
        title=title,
        content=content,
        actions=card_actions,
        dismissible=True,
    )

    return f"CARD:{descriptor.descriptor_id}"


def request_confirmation(action_description: str, risk_level: str = "medium") -> str:
    """Request user confirmation for an action.

    Returns: UI descriptor ID
    """
    from ui.descriptors.confirmation import ConfirmationDescriptor

    descriptor = ConfirmationDescriptor(
        descriptor_id=str(uuid4()),
        title="Confirmation Required",
        message=action_description,
        confirm_text="Confirm",
        cancel_text="Cancel",
        risk_level=risk_level,
    )

    return f"CONFIRMATION:{descriptor.descriptor_id}"


def update_progress(task_name: str, progress_percent: int) -> str:
    """Update a progress indicator for a long-running task.

    Returns: UI descriptor ID
    """
    from ui.descriptors.progress import ProgressDescriptor

    descriptor = ProgressDescriptor(
        descriptor_id=str(uuid4()),
        task_name=task_name,
        progress_percent=progress_percent,
        status_text=f"In progress: {progress_percent}%",
        indeterminate=False,
    )

    return f"PROGRESS:{descriptor.descriptor_id}"
```

---

## 1.5 API Contract

### Integration with Main Agent

The UIDSPyAgent is exposed as a tool to the MainDSPyReActAgent:

```python
# In MainDSPyReActAgent
ui_agent = UIDSPyAgent()
ui_tool = dspy.Tool(
    ui_agent.show_card,
    name="show_card",
    desc="Generate a card widget with title and content"
)
```

### Descriptor ID Format

All UI tools return descriptor IDs in the format:
```
{DESCRIPTOR_TYPE}:{uuid}
```

Examples:
- `MARKDOWN_BLOCK:550e8400-e29b-41d4-a716-446655440000`
- `CARD:550e8400-e29b-41d4-a716-446655440001`
- `CONFIRMATION:550e8400-e29b-41d4-a716-446655440002`
- `PROGRESS:550e8400-e29b-41d4-a716-446655440003`

---

## 1.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| **BR-UI-001** | Agent MUST NOT generate HTML or CSS | Code review |
| **BR-UI-002** | All tools MUST return descriptor IDs only | Code review + tests |
| **BR-UI-003** | Descriptor types MUST match C002 enum values | Code validation |
| **BR-UI-004** | Risk level MUST be one of: low, medium, high | Enum validation |
| **BR-UI-005** | Progress percent MUST be between 0 and 100 | Range validation |

---

## 1.7 Acceptance Criteria

- [ ] UIDSPyAgent compiles without errors
- [ ] All 6 signatures implemented (SelectWidget, ConfigureForm, ShowCard, RequestConfirmation, UpdateProgress)
- [ ] All UI tools return descriptor IDs (not full objects)
- [ ] No HTML or CSS generation in any tool
- [ ] Integration with C002 descriptors works
- [ ] File under 80 lines
- [ ] Widget selection returns valid descriptor types
- [ ] Form configuration generates valid field definitions
- [ ] Confirmation dialog includes risk level

---

**Related Specs**:
- `specs/dspy-main-agent/spec.md` - Main agent orchestration
- `specs/dspy-rag-agent/spec.md` - RAG specialist agent
- C002 data contracts - UI descriptor definitions

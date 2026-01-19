# T301: Create UI DSPy Signatures

**Phase**: 3
**Estimated Time**: 25 minutes
**Dependencies**: T001, T300
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/agent_runtime.md` - UI DSPy signatures
- `lld/ui_descriptor_contract.md` - UI widget types
- `lld/incremental_release_plan.md` - Phase 3: UI agent signatures

**Description**:
Creates DSPy signatures for UI generation. These signatures enable the UI agent to select appropriate widgets and configure them based on content.

---

## Acceptance Criteria

**Passing Criteria**:
- agent/dspy_signatures/ui_signatures.py exists
- SelectWidgetSignature defined
- ConfigureFormSignature defined
- ShowCardSignature defined
- RequestConfirmationSignature defined
- All signatures can be imported

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify file exists
test -f agentx/agent/dspy_signatures/ui_signatures.py && echo "UI signatures exist"

# Verify import works
python3 -c "from agentx.agent.dspy_signatures.ui_signatures import SelectWidgetSignature; print('Import OK')"
```

---

## Implementation Steps

### Step 1: Create UI DSPy signatures

Create file `agentx/agent/dspy_signatures/ui_signatures.py`:

```python
"""UI DSPy signatures for generative UI."""

import dspy
from typing import List


class SelectWidgetSignature(dspy.Signature):
    """Select the appropriate UI widget for displaying content.

    This signature analyzes content type and context to determine which
    UI widget type should be used (markdown, card, form, etc.).
    """

    content_type: str = dspy.InputField(desc="Type of content to display (text, data, form, etc.)")
    context: str = dspy.InputField(desc="Additional context for widget selection")
    user_goal: str = dspy.InputField(desc="What the user is trying to accomplish", default="")
    widget_type: str = dspy.OutputField(desc="Selected widget type (markdown_block, card, form, progress, action, confirmation, voice)")
    widget_rationale: str = dspy.OutputField(desc="Explanation for widget selection")


class ConfigureFormSignature(dspy.Signature):
    """Configure a form schema for user input.

    This signature generates form fields based on required information.
    """

    required_fields: str = dspy.InputField(desc="Comma-separated list of fields needed from user")
    context: str = dspy.InputField(desc="Context for what the form is for")
    form_title: str = dspy.OutputField(desc="Title for the form")
    form_fields_json: str = dspy.OutputField(desc="JSON array of form field definitions")
    submit_text: str = dspy.OutputField(desc="Submit button text")


class ShowCardSignature(dspy.Signature):
    """Generate a card widget with title and content.

    This signature creates structured card widgets for displaying information.
    """

    title: str = dspy.InputField(desc="Card title")
    content: str = dspy.InputField(desc="Card content (markdown supported)")
    context: str = dspy.InputField(desc="Additional context for card styling", default="")
    actions: str = dspy.OutputField(desc="JSON array of action buttons (optional)")
    card_variant: str = dspy.OutputField(desc="Visual variant (default, outlined, elevated)")


class RequestConfirmationSignature(dspy.Signature):
    """Request user confirmation for an action.

    This signature generates confirmation dialogs for risky operations.
    """

    action_description: str = dspy.InputField(desc="Description of action to confirm")
    risk_level: str = dspy.InputField(desc="Risk level (low, medium, high)")
    context: str = dspy.InputField(desc="Additional context", default="")
    confirmation_title: str = dspy.OutputField(desc="Dialog title")
    confirmation_message: str = dspy.OutputField(desc="Confirmation message")
    confirm_button_text: str = dspy.OutputField(desc="Confirm button text")
    is_dangerous: bool = dspy.OutputField(desc="Whether this is a dangerous action")


class UpdateProgressSignature(dspy.Signature):
    """Update a progress indicator for a long-running task.

    This signature generates progress updates for background operations.
    """

    task_name: str = dspy.InputField(desc="Name of the task being performed")
    current_step: str = dspy.InputField(desc="Current step description")
    total_steps: int = dspy.InputField(desc="Total number of steps", default=0)
    current_step_number: int = dspy.InputField(desc="Current step number (1-indexed)", default=1)
    progress_title: str = dspy.OutputField(desc="Progress title")
    progress_percent: int = dspy.OutputField(desc="Progress percentage (0-100)")
    status_text: str = dspy.OutputField(desc="Current status text")
    indeterminate: bool = dspy.OutputField(desc="Show indeterminate progress")
```

### Step 2: Update dspy_signatures __init__.py

Update file `agentx/agent/dspy_signatures/__init__.py`:

```python
"""DSPy signatures for AGENTX agents."""

from agentx.agent.dspy_signatures.main_signatures import (
    MainAgentSignature,
    ToolSelectionSignature,
    ConfidenceScoringSignature,
)
from agentx.agent.dspy_signatures.ui_signatures import (
    SelectWidgetSignature,
    ConfigureFormSignature,
    ShowCardSignature,
    RequestConfirmationSignature,
    UpdateProgressSignature,
)

__all__ = [
    "MainAgentSignature",
    "ToolSelectionSignature",
    "ConfidenceScoringSignature",
    "SelectWidgetSignature",
    "ConfigureFormSignature",
    "ShowCardSignature",
    "RequestConfirmationSignature",
    "UpdateProgressSignature",
]
```

---

## Expected Failures & Countermeasures

### Failure: DSPy signatures fail to compile

**Likelihood**: Low
**Symptoms**: DSPy compilation error on signature usage

**Countermeasures**:
1. Ensure all InputFields have desc parameter
2. Ensure all OutputFields have desc parameter
3. Check field types are correct (str, int, bool, float)
4. Verify dspy module is imported

**Recovery Time**: 5 minutes

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T300 descriptors changed
**Detection**: Descriptor types don't match enum values
**Action**: Update signature descriptions to match descriptor types

**Recovery Time**: 5 minutes

### Downstream Impact

**Scenario**: Signature field names change
**Prevention**: All signature field names are LOCKED
**Mitigation**: Update UI agent and all use sites
**Affected Tasks**: T302 (UI DSPy Agent), T304 (Tests)

---

## Artifacts

**Files Created**:
- `agentx/agent/dspy_signatures/ui_signatures.py` (UI signatures, LOCKED)

**Files Modified**:
- `agentx/agent/dspy_signatures/__init__.py` (Add exports)

**Locked APIs**:
- All UI signature class names
- All signature field names and types
- Widget type values in SelectWidgetSignature

---

## Quality Gates

**Quality Checks**:
- **Check**: UI signatures file exists
  - Command: `test -f agentx/agent/dspy_signatures/ui_signatures.py && echo "OK"`
  - Expected: `OK`
  - Required: Yes

- **Check**: UI signatures can be imported
  - Command: `python3 -c "from agentx.agent.dspy_signatures.ui_signatures import SelectWidgetSignature, ConfigureFormSignature; print('OK')"`
  - Expected: `OK`
  - Required: Yes

---

## Notes

1. UI signatures enable generative UI
2. SelectWidgetSignature maps content to widget type
3. ConfigureFormSignature generates form fields dynamically
4. ShowCardSignature creates structured information cards
5. RequestConfirmationSignature handles risky operations
6. UpdateProgressSignature tracks long-running tasks
7. All signatures have descriptive fields for LLM guidance

---

## Completion Checklist

- [ ] ui_signatures.py created with all signatures
- [ ] SelectWidgetSignature defined
- [ ] ConfigureFormSignature defined
- [ ] ShowCardSignature defined
- [ ] RequestConfirmationSignature defined
- [ ] UpdateProgressSignature defined
- [ ] __init__.py updated with exports
- [ ] All signatures can be imported
- [ ] Ready for T302 (UI DSPy Agent)

---

**Task T301 is part of Phase 3: UI DSPy Agent + Descriptors**
**Locked APIs**: All UI signature class names, field names, and types

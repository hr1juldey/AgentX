# T302: Create UI DSPy Agent

**Phase**: 3
**Estimated Time**: 35 minutes
**Dependencies**: T001, T300, T301
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/agent_runtime.md` - UI DSPy agent definition
- `lld/ui_descriptor_contract.md` - UI descriptor types
- `lld/incremental_release_plan.md` - Phase 3: UI agent

**Description**:
Creates UI DSPy agent that generates UI descriptors based on content. This agent uses UI-specific signatures to create widgets.

---

## Acceptance Criteria

**Passing Criteria**:
- UIDSPyAgent class exists
- Uses UI DSPy signatures (SelectWidget, ConfigureForm, etc.)
- Has methods to generate each descriptor type
- Returns Pydantic descriptor models
- Can be imported

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify file exists
test -f agentx/agent/dspy_agents/ui_dspy_agent.py && echo "UI agent exists"

# Verify import works
python3 -c "from agentx.agent.dspy_agents.ui_dspy_agent import UIDSPyAgent; print('Import OK')"
```

---

## Implementation Steps

### Step 1: Create UI DSPy agent

Create file `agentx/agent/dspy_agents/ui_dspy_agent.py`:

```python
"""UI DSPy agent for generative UI."""

import json
import dspy
from typing import Optional
from uuid import uuid4

from agentx.agent.dspy_signatures import (
    SelectWidgetSignature,
    ConfigureFormSignature,
    ShowCardSignature,
    RequestConfirmationSignature,
    UpdateProgressSignature,
)
from agentx.ui.descriptors import (
    UIDescriptorType,
    MarkdownBlockDescriptor,
    CardDescriptor,
    CardAction,
    FormDescriptor,
    FormField,
    ProgressDescriptor,
    ActionDescriptor,
    ConfirmationDescriptor,
)


class UIDSPyAgent(dspy.Module):
    """UI agent for generating UI descriptors.

    This agent uses DSPy to select appropriate widgets and configure them
    based on content and context.

    Example:
        >>> agent = UIDSPyAgent()
        >>> descriptor = agent.create_markdown_block("Hello, world!")
        >>> assert isinstance(descriptor, MarkdownBlockDescriptor)
    """

    def __init__(self):
        super().__init__()
        # Initialize DSPy predictors
        self.widget_selector = dspy.Predict(SelectWidgetSignature)
        self.form_configurer = dspy.Predict(ConfigureFormSignature)
        self.card_generator = dspy.Predict(ShowCardSignature)
        self.confirmation_generator = dspy.Predict(RequestConfirmationSignature)
        self.progress_updater = dspy.Predict(UpdateProgressSignature)

    def create_markdown_block(
        self,
        content: str,
        display_name: Optional[str] = None
    ) -> MarkdownBlockDescriptor:
        """Create a markdown text block descriptor.

        Args:
            content: Markdown content
            display_name: Optional display name

        Returns:
            MarkdownBlockDescriptor
        """
        return MarkdownBlockDescriptor(
            descriptor_id=str(uuid4()),
            descriptor_type=UIDescriptorType.MARKDOWN_BLOCK,
            display_name=display_name,
            content=content
        )

    def create_card(
        self,
        title: str,
        content: str,
        actions: Optional[list] = None,
        display_name: Optional[str] = None
    ) -> CardDescriptor:
        """Create a card widget descriptor.

        Args:
            title: Card title
            content: Card content (markdown)
            actions: Optional list of action dicts
            display_name: Optional display name

        Returns:
            CardDescriptor
        """
        card_actions = []
        if actions:
            for action in actions:
                card_actions.append(CardAction(
                    action_id=action.get("action_id", str(uuid4())),
                    label=action.get("label", "Action"),
                    variant=action.get("variant", "primary")
                ))

        return CardDescriptor(
            descriptor_id=str(uuid4()),
            descriptor_type=UIDescriptorType.CARD,
            display_name=display_name,
            title=title,
            content=content,
            actions=card_actions
        )

    def create_form(
        self,
        fields: list,
        title: Optional[str] = None,
        description: Optional[str] = None,
        submit_text: str = "Submit"
    ) -> FormDescriptor:
        """Create a form descriptor.

        Args:
            fields: List of field definitions
            title: Optional form title
            description: Optional form description
            submit_text: Submit button text

        Returns:
            FormDescriptor
        """
        form_fields = []
        for field in fields:
            form_fields.append(FormField(
                field_name=field.get("field_name", str(uuid4())),
                field_type=field.get("field_type", "text"),
                label=field.get("label", "Field"),
                placeholder=field.get("placeholder"),
                required=field.get("required", False),
                default_value=field.get("default_value"),
                options=field.get("options")
            ))

        return FormDescriptor(
            descriptor_id=str(uuid4()),
            descriptor_type=UIDescriptorType.FORM,
            form_id=str(uuid4()),
            title=title,
            description=description,
            fields=form_fields,
            submit_button_text=submit_text
        )

    def create_progress(
        self,
        task_name: str,
        progress_percent: int,
        status_text: Optional[str] = None,
        indeterminate: bool = False
    ) -> ProgressDescriptor:
        """Create a progress indicator descriptor.

        Args:
            task_name: Name of the task
            progress_percent: Progress percentage (0-100)
            status_text: Optional status text
            indeterminate: Show indeterminate progress

        Returns:
            ProgressDescriptor
        """
        return ProgressDescriptor(
            descriptor_id=str(uuid4()),
            descriptor_type=UIDescriptorType.PROGRESS,
            task_name=task_name,
            progress_percent=progress_percent,
            status_text=status_text,
            indeterminate=indeterminate
        )

    def create_action(
        self,
        button_text: str,
        action_id: str,
        variant: str = "primary",
        display_name: Optional[str] = None
    ) -> ActionDescriptor:
        """Create an action button descriptor.

        Args:
            button_text: Button label
            action_id: Action identifier
            variant: Visual style
            display_name: Optional display name

        Returns:
            ActionDescriptor
        """
        return ActionDescriptor(
            descriptor_id=str(uuid4()),
            descriptor_type=UIDescriptorType.ACTION,
            display_name=display_name,
            button_text=button_text,
            action_id=action_id,
            variant=variant
        )

    def create_confirmation(
        self,
        title: str,
        message: str,
        confirm_text: str = "Confirm",
        risk_level: str = "medium",
        display_name: Optional[str] = None
    ) -> ConfirmationDescriptor:
        """Create a confirmation dialog descriptor.

        Args:
            title: Dialog title
            message: Confirmation message
            confirm_text: Confirm button text
            risk_level: Risk level (low, medium, high)
            display_name: Optional display name

        Returns:
            ConfirmationDescriptor
        """
        return ConfirmationDescriptor(
            descriptor_id=str(uuid4()),
            descriptor_type=UIDescriptorType.CONFIRMATION,
            display_name=display_name,
            title=title,
            message=message,
            confirm_text=confirm_text,
            risk_level=risk_level,
            dangerous=(risk_level == "high")
        )

    def select_widget_for_content(
        self,
        content_type: str,
        context: str,
        user_goal: str = ""
    ) -> str:
        """Select appropriate widget type for content.

        Args:
            content_type: Type of content
            context: Additional context
            user_goal: User's goal

        Returns:
            Widget type string
        """
        try:
            result = self.widget_selector(
                content_type=content_type,
                context=context,
                user_goal=user_goal
            )
            return result.widget_type
        except Exception:
            # Fallback to markdown if DSPy fails
            return "markdown_block"


def get_ui_agent() -> UIDSPyAgent:
    """Get or create UI agent instance.

    Returns:
        UIDSPyAgent instance
    """
    return UIDSPyAgent()
```

### Step 2: Update dspy_agents __init__.py

Update file `agentx/agent/dspy_agents/__init__.py`:

```python
"""DSPy agents for AGENTX."""

from agentx.agent.dspy_agents.main_react_agent import (
    MainDSPyReActAgent,
    AgentFactory,
    get_main_agent,
)
from agentx.agent.dspy_agents.ui_dspy_agent import (
    UIDSPyAgent,
    get_ui_agent,
)

__all__ = [
    "MainDSPyReActAgent",
    "AgentFactory",
    "get_main_agent",
    "UIDSPyAgent",
    "get_ui_agent",
]
```

---

## Expected Failures & Countermeasures

### Failure: Descriptor import errors

**Likelihood**: Low
**Symptoms**: `ModuleNotFoundError: No module named 'ui.descriptors'`

**Countermeasures**:
1. Ensure T300 (UI Descriptor Schemas) is complete
2. Check ui/descriptors/__init__.py exports all descriptors
3. Verify descriptor files exist

**Recovery Time**: 5 minutes

### Failure: DSPy predictor fails

**Likelihood**: Medium
**Symptoms**: select_widget_for_content() raises exception

**Countermeasures**:
1. Method catches exceptions and returns fallback "markdown_block"
2. Ensure Ollama is running for DSPy to work
3. Check UI signatures are correctly defined

**Recovery Time**: 0 minutes (graceful fallback)

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T300 descriptors changed
**Detection**: Descriptor field names don't match
**Action**: Update agent to use new descriptor fields

**Recovery Time**: 10 minutes

**Scenario**: T301 signatures changed
**Detection**: Signature field names don't match
**Action**: Update agent to use new signature fields

**Recovery Time**: 5 minutes

### Downstream Impact

**Scenario**: UIDSPyAgent method names change
**Prevention**: All method names are LOCKED
**Mitigation**: Update all use sites
**Affected Tasks**: T303 (WebSocket), T304 (Tests), Phase 6 (Frontend)

---

## Artifacts

**Files Created**:
- `agentx/agent/dspy_agents/ui_dspy_agent.py` (UI agent, LOCKED)

**Files Modified**:
- `agentx/agent/dspy_agents/__init__.py` (Add exports)

**Locked APIs**:
- `UIDSPyAgent` class name
- All method names (create_markdown_block, create_card, etc.)
- All method signatures
- `get_ui_agent()` function signature

---

## Quality Gates

**Quality Checks**:
- **Check**: UI agent file exists
  - Command: `test -f agentx/agent/dspy_agents/ui_dspy_agent.py && echo "OK"`
  - Expected: `OK`
  - Required: Yes

- **Check**: UI agent can be imported
  - Command: `python3 -c "from agentx.agent.dspy_agents.ui_dspy_agent import UIDSPyAgent; print('OK')"`
  - Expected: `OK`
  - Required: Yes

- **Check**: UI agent can be instantiated
  - Command: `python3 -c "from agentx.agent.dspy_agents.ui_dspy_agent import UIDSPyAgent; a = UIDSPyAgent(); print(type(a).__name__)"`
  - Expected: `UIDSPyAgent`
  - Required: Yes

---

## Notes

1. UI agent generates Pydantic descriptor models
2. Each create_* method returns specific descriptor type
3. select_widget_for_content uses DSPy to choose widget
4. Graceful fallback if DSPy fails
5. All descriptors have unique IDs (uuid4)
6. Display names are optional

---

## Completion Checklist

- [ ] ui_dspy_agent.py created
- [ ] UIDSPyAgent class defined with all methods
- [ ] create_markdown_block() implemented
- [ ] create_card() implemented
- [ ] create_form() implemented
- [ ] create_progress() implemented
- [ ] create_action() implemented
- [ ] create_confirmation() implemented
- [ ] select_widget_for_content() implemented
- [ ] get_ui_agent() factory function
- [ ] __init__.py updated
- [ ] All imports work
- [ ] Ready for T303 (WebSocket Streaming)

---

**Task T302 is part of Phase 3: UI DSPy Agent + Descriptors**
**Locked APIs**: UIDSPyAgent class name, all method names and signatures

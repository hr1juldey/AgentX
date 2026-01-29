"""UI generation signatures for UIDSPyAgent.

Locked from LLD: agent_runtime.md:58-109

These signatures enable the UI specialist agent to generate UI descriptors
for displaying content to users. The agent returns descriptor IDs, not
full descriptor objects (returned by UIService).
"""

import dspy
from typing import Dict, Any, List


class ConfigureFormSignature(dspy.Signature):
    """Configure a form schema for user input.

    Generates form field definitions based on required information.
    Returns descriptor ID (format: FORM:{uuid}).
    """

    required_fields: List[str] = dspy.InputField(
        desc="Fields required from user (e.g., ['name', 'email'])",
        prefix="Fields: ",
    )
    context: str = dspy.InputField(
        desc="Context for form configuration (why this info is needed)",
        prefix="Context: ",
    )
    form_schema: Dict[str, Any] = dspy.OutputField(
        desc="Form schema definition with field types and validation",
        prefix="Schema: ",
    )


class ShowCardSignature(dspy.Signature):
    """Generate a card widget with title and content.

    Creates a structured card widget for presenting information.
    Returns descriptor ID (format: CARD:{uuid}).
    """

    title: str = dspy.InputField(
        desc="Card title (brief, descriptive)",
        prefix="Title: ",
    )
    content: str = dspy.InputField(
        desc="Card content (markdown supported)",
        prefix="Content: ",
    )
    context: str = dspy.InputField(
        desc="Additional context for card configuration",
        prefix="Context: ",
    )
    show_actions: bool = dspy.OutputField(
        desc="Whether to show action buttons on the card",
        prefix="Actions: ",
    )
    card_descriptor: Dict[str, Any] = dspy.OutputField(
        desc="Card widget descriptor configuration",
        prefix="Descriptor: ",
    )


class RequestConfirmationSignature(dspy.Signature):
    """Request user confirmation for an action.

    Generates a confirmation dialog with risk assessment.
    Returns descriptor ID (format: CONFIRMATION:{uuid}).
    """

    action_description: str = dspy.InputField(
        desc="Description of action to confirm",
        prefix="Action: ",
    )
    risk_level: str = dspy.InputField(
        desc="Risk level: low, medium, high",
        prefix="Risk: ",
    )
    confirmation_dialog: Dict[str, Any] = dspy.OutputField(
        desc="Confirmation dialog descriptor",
        prefix="Dialog: ",
    )


class UpdateProgressSignature(dspy.Signature):
    """Update a progress indicator for a long-running task.

    Generates or updates a progress widget.
    Returns descriptor ID (format: PROGRESS:{uuid}).
    """

    task_name: str = dspy.InputField(
        desc="Name of the task being tracked",
        prefix="Task: ",
    )
    current_step: int = dspy.InputField(
        desc="Current step number (1-indexed)",
        prefix="Step: ",
    )
    total_steps: int = dspy.InputField(
        desc="Total number of steps",
        prefix="Total: ",
    )
    progress_descriptor: Dict[str, Any] = dspy.OutputField(
        desc="Progress widget descriptor with percent and status",
        prefix="Progress: ",
    )

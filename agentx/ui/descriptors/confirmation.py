"""Confirmation descriptor for Real AgentX v0.1.

Confirmation dialog with confirm/cancel buttons.
"""

from pydantic import Field
from typing import Any

from agentx.ui.descriptors.base import BaseUIDescriptor, UIDescriptorType


class ConfirmationDescriptor(BaseUIDescriptor):
    """Confirmation dialog widget descriptor.

    Displays a confirmation prompt with confirm/cancel actions.
    """

    descriptor_id: str = Field(alias="id")
    descriptor_type: UIDescriptorType = Field(default=UIDescriptorType.CONFIRMATION)
    title: str = Field(description="Dialog title")
    message: str = Field(description="Confirmation message")
    confirm_label: str = Field(default="Confirm", description="Confirm button label")
    cancel_label: str = Field(default="Cancel", description="Cancel button label")
    on_confirm: str = Field(description="Action to execute on confirm")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    class Config:
        populate_by_name = True

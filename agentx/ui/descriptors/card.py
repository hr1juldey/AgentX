"""Card descriptor for Real AgentX v0.1.

Card component with title, content, actions.
"""

from pydantic import BaseModel, Field
from typing import Any, List

from agentx.ui.descriptors.base import BaseUIDescriptor, UIDescriptorType


class CardAction(BaseModel):
    """Action button on a card."""

    label: str = Field(description="Button label")
    action: str = Field(description="Action identifier")
    variant: str = Field(default="outline", description="Button style (outline/solid)")


class CardDescriptor(BaseUIDescriptor):
    """Card widget descriptor.

    Displays content with optional action buttons.
    """

    descriptor_id: str = Field(alias="id")
    descriptor_type: UIDescriptorType = Field(default=UIDescriptorType.CARD)
    title: str = Field(description="Card title")
    content: str = Field(description="Card body content (markdown supported)")
    actions: List[CardAction] = Field(default_factory=list, description="Action buttons")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        populate_by_name = True

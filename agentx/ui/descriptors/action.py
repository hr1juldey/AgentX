"""Action descriptor for Real AgentX v0.1.

Action button widget descriptor.
"""

from pydantic import BaseModel, Field
from typing import Any

from agentx.ui.descriptors.base import BaseUIDescriptor, UIDescriptorType


class ActionDescriptor(BaseUIDescriptor):
    """Action button widget descriptor.

    Displays a clickable action button.
    """

    descriptor_id: str = Field(alias="id")
    descriptor_type: UIDescriptorType = Field(default=UIDescriptorType.ACTION)
    label: str = Field(description="Button label")
    action: str = Field(description="Action identifier")
    primary: bool = Field(default=True, description="Whether button is primary style")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        populate_by_name = True

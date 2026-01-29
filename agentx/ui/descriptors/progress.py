"""Progress descriptor for Real AgentX v0.1.

Progress indicator with percentage and status.
"""

from pydantic import BaseModel, Field
from typing import Any

from agentx.ui.descriptors.base import BaseUIDescriptor, UIDescriptorType


class ProgressDescriptor(BaseUIDescriptor):
    """Progress widget descriptor.

    Displays progress with percentage and status message.
    """

    descriptor_id: str = Field(alias="id")
    descriptor_type: UIDescriptorType = Field(default=UIDescriptorType.PROGRESS)
    progress: int = Field(default=0, ge=0, le=100, description="Progress percentage (0-100)")
    status: str = Field(description="Status message")
    indeterminate: bool = Field(default=False, description="Whether progress is indeterminate")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        populate_by_name = True

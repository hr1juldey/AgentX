"""Voice descriptor for Real AgentX v0.1.

Voice input/output widget descriptor.
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Any

from agentx.ui.descriptors.base import BaseUIDescriptor, UIDescriptorType


class VoiceState(str, Enum):
    """Voice widget states."""

    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"


class VoiceDescriptor(BaseUIDescriptor):
    """Voice widget descriptor.

    Displays voice input/output with transcript.
    """

    descriptor_id: str = Field(alias="id")
    descriptor_type: UIDescriptorType = Field(default=UIDescriptorType.VOICE)
    state: VoiceState = Field(default=VoiceState.IDLE, description="Current voice state")
    transcript: str = Field(default="", description="Voice transcript text")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        populate_by_name = True

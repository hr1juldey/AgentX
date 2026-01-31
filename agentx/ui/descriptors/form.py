"""Form descriptor for Real AgentX v0.1.

Form with input fields and submission handling.
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, List

from agentx.ui.descriptors.base import BaseUIDescriptor, UIDescriptorType


class FormFieldType(str, Enum):
    """Form field types."""

    TEXT = "text"
    EMAIL = "email"
    PASSWORD = "password"
    NUMBER = "number"
    TEXTAREA = "textarea"
    SELECT = "select"
    CHECKBOX = "checkbox"
    RADIO = "radio"


class FormField(BaseModel):
    """Form field definition."""

    name: str = Field(description="Field name (identifier)")
    label: str = Field(description="Field label (display text)")
    field_type: FormFieldType = Field(description="Field type")
    placeholder: str = Field(default="", description="Placeholder text")
    required: bool = Field(default=False, description="Whether field is required")
    options: List[str] = Field(
        default_factory=list, description="Options for select/radio"
    )
    default_value: Any = Field(default=None, description="Default value")


class FormDescriptor(BaseUIDescriptor):
    """Form widget descriptor.

    Displays a form with multiple input fields.
    """

    descriptor_id: str = Field(alias="id")
    descriptor_type: UIDescriptorType = Field(default=UIDescriptorType.FORM)
    title: str = Field(description="Form title")
    fields: List[FormField] = Field(description="Form fields")
    submit_url: str = Field(description="URL to submit form to")
    method: str = Field(default="POST", description="HTTP method (GET/POST)")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    class Config:
        populate_by_name = True

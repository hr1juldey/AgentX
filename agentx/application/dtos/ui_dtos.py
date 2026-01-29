"""UI DTOs for Real AgentX v0.1.

Data Transfer Objects for UI-related API operations.
"""

from typing import Any

from pydantic import BaseModel, Field


class UIComponentDTO(BaseModel):
    """DTO for UI component in server-driven UI pattern."""

    component_id: str = Field(..., description="Component identifier")
    component_type: str = Field(..., description="Component type")
    props: dict[str, Any] = Field(default_factory=dict, description="Component props")
    merge: bool = Field(False, description="Merge with existing component")


class MarkdownComponentDTO(UIComponentDTO):
    """DTO for markdown component."""

    content: str = Field(..., description="Markdown content")
    format: str = Field("markdown", description="Content format")


class CardComponentDTO(UIComponentDTO):
    """DTO for card component."""

    title: str = Field(..., description="Card title")
    content: str = Field(..., description="Card content")
    actions: list[dict[str, Any]] = Field(
        default_factory=list, description="Action buttons"
    )


class FormComponentDTO(UIComponentDTO):
    """DTO for form component."""

    fields: list[dict[str, Any]] = Field(..., description="Form fields")
    submit_url: str = Field(..., description="Form submission endpoint")
    method: str = Field("POST", description="HTTP method")


class ProgressComponentDTO(UIComponentDTO):
    """DTO for progress component."""

    progress: int = Field(..., ge=0, le=100, description="Progress percentage")
    status: str = Field(..., description="Status text")
    indeterminate: bool = Field(False, description="Indeterminate progress")


class ActionComponentDTO(UIComponentDTO):
    """DTO for action button component."""

    label: str = Field(..., description="Button label")
    action: str = Field(..., description="Action identifier")
    primary: bool = Field(True, description="Primary button style")


class ConfirmationComponentDTO(UIComponentDTO):
    """DTO for confirmation dialog component."""

    title: str = Field(..., description="Dialog title")
    message: str = Field(..., description="Confirmation message")
    confirm_label: str = Field("Confirm", description="Confirm button label")
    cancel_label: str = Field("Cancel", description="Cancel button label")
    on_confirm: str = Field(..., description="Action on confirm")


class VoiceComponentDTO(UIComponentDTO):
    """DTO for voice component."""

    state: str = Field(
        ..., description="Voice state (idle, listening, processing, speaking)"
    )
    transcript: str = Field("", description="Current transcript")


class ImageComponentDTO(UIComponentDTO):
    """DTO for image component."""

    url: str = Field(..., description="Image URL")
    alt: str = Field("", description="Alt text")
    caption: str = Field("", description="Image caption")


class GalleryComponentDTO(UIComponentDTO):
    """DTO for image gallery component."""

    images: list[dict[str, Any]] = Field(..., description="Image items")
    columns: int = Field(3, ge=1, le=6, description="Number of columns")


class ChartComponentDTO(UIComponentDTO):
    """DTO for chart component."""

    chart_type: str = Field(..., description="Chart type (line, bar, pie)")
    data: dict[str, Any] = Field(..., description="Chart data")
    options: dict[str, Any] = Field(default_factory=dict, description="Chart options")


class SearchResultComponentDTO(UIComponentDTO):
    """DTO for search result component."""

    query: str = Field(..., description="Search query")
    results: list[dict[str, Any]] = Field(..., description="Search results")


class HopProgressComponentDTO(UIComponentDTO):
    """DTO for multi-hop RAG progress component."""

    current_hop: int = Field(..., description="Current hop number")
    total_hops: int = Field(..., description="Total number of hops")
    hop_status: list[dict[str, Any]] = Field(..., description="Status of each hop")


class CitationCardComponentDTO(UIComponentDTO):
    """DTO for citation card component."""

    source: str = Field(..., description="Source name")
    content: str = Field(..., description="Cited content")
    url: str = Field("", description="Source URL")
    relevance: float = Field(..., ge=0, le=1, description="Relevance score")

"""Domain models for widget selection.

This module defines the models for adaptive widget selection
based on accumulated research findings.
"""

from enum import Enum

from pydantic import BaseModel, Field


class WidgetType(str, Enum):
    """Types of widgets for UI."""

    DATA_TABLE = "data_table"
    CHART = "chart"
    TIMELINE = "timeline"
    MAP = "map"
    TEXT_CARD = "text_card"


class ContentPattern(str, Enum):
    """Content patterns detected in research findings."""

    COMPARISON = "comparison"
    TEMPORAL = "temporal"
    GEOGRAPHIC = "geographic"
    RANKING = "ranking"
    NUMERICAL = "numerical"
    TEXTUAL = "textual"


class WidgetSpecification(BaseModel):
    """Specification for a UI widget."""

    widget_type: WidgetType = Field(description="Type of widget")
    title: str = Field(description="Widget title")
    content: dict = Field(
        default_factory=dict,
        description="Widget-specific content",
    )
    priority: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Widget priority for sorting (1=lowest, 10=highest)",
    )
    sources: list[str] = Field(
        default_factory=list,
        description="Source attributions",
    )

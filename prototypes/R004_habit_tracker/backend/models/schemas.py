# =============================================================================
# R004 Habit Tracker - Pydantic Models
# =============================================================================
# Request/response schemas for Habit Tracker API endpoints
# =============================================================================

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class HabitFrequency(str, Enum):
    """Habit frequency options."""

    DAILY = "daily"
    WEEKLY = "weekly"


class HabitCreate(BaseModel):
    """Schema for creating a habit."""

    name: str = Field(..., description="Habit name", min_length=1, max_length=200)
    description: str | None = Field(None, description="Optional habit description")
    frequency: HabitFrequency = Field(
        default=HabitFrequency.DAILY, description="How often the habit should be done"
    )
    target_count: int = Field(
        default=1,
        description="Number of times per frequency period",
        ge=1,
        le=100,
    )


class HabitResponse(BaseModel):
    """Schema for habit response."""

    id: int = Field(..., description="Habit ID")
    name: str = Field(..., description="Habit name")
    description: str | None = Field(..., description="Habit description")
    frequency: HabitFrequency = Field(..., description="Habit frequency")
    target_count: int = Field(..., description="Target count per period")
    streak_count: int = Field(..., description="Current streak count", ge=0)
    total_completions: int = Field(..., description="Total completions all time", ge=0)
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class HabitCompletionCreate(BaseModel):
    """Schema for creating a habit completion."""

    habit_id: int = Field(..., description="Habit ID")
    completed_at: datetime | None = Field(
        None, description="When the habit was completed (defaults to now)"
    )
    notes: str | None = Field(None, description="Optional notes about this completion")


class HabitCompletionResponse(BaseModel):
    """Schema for habit completion response."""

    id: int = Field(..., description="Completion ID")
    habit_id: int = Field(..., description="Habit ID")
    completed_at: datetime = Field(..., description="Completion timestamp")
    notes: str | None = Field(..., description="Completion notes")


class StreakData(BaseModel):
    """Schema for streak information."""

    current_streak: int = Field(..., description="Current streak count", ge=0)
    longest_streak: int = Field(..., description="Longest streak count", ge=0)
    last_completion_date: datetime | None = Field(
        None, description="Date of last completion"
    )


class HabitDetailResponse(HabitResponse):
    """Schema for habit detail with completion history."""

    completions: list[HabitCompletionResponse] = Field(
        default_factory=list, description="List of completions"
    )
    streak_data: StreakData = Field(..., description="Streak information")


class TimeSeriesData(BaseModel):
    """Schema for time-series aggregated data."""

    date: str = Field(..., description="Date in YYYY-MM-DD format")
    count: int = Field(..., description="Number of completions", ge=0)


class HabitListResponse(BaseModel):
    """Schema for habit list response."""

    habits: list[HabitResponse] = Field(default_factory=list, description="List of habits")
    total: int = Field(..., description="Total count of habits")


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Detailed error information")

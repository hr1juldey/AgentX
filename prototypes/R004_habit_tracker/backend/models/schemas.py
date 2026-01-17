# =============================================================================
# R004 Habit Tracker - Pydantic Models
# =============================================================================
# Request/response schemas for Habit Tracker API endpoints with enhanced Swagger docs
# =============================================================================

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class HabitFrequency(str, Enum):
    """Habit frequency options.

    How often a habit should be completed.
    """

    DAILY = "daily"
    WEEKLY = "weekly"


class HabitCreate(BaseModel):
    """Schema for creating a new habit.

    Define a habit with frequency and completion targets.
    """

    name: str = Field(
        ...,
        description="Habit name (brief, action-oriented)",
        min_length=1,
        max_length=200,
        examples=["Morning meditation", "Exercise", "Read 30 minutes"],
    )
    description: str | None = Field(
        None,
        description="Optional habit description or motivation",
        examples=["Clears mind and sets positive tone for the day"],
    )
    frequency: HabitFrequency = Field(
        default=HabitFrequency.DAILY,
        description="How often to perform this habit",
        examples=[HabitFrequency.DAILY, HabitFrequency.WEEKLY],
    )
    target_count: int = Field(
        default=1,
        description="Number of times per frequency period",
        ge=1,
        le=100,
        examples=[1, 3, 7],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Morning meditation",
                    "description": "Clears mind and sets positive tone",
                    "frequency": "daily",
                    "target_count": 1,
                }
            ]
        }
    }


class HabitResponse(BaseModel):
    """Schema for habit response.

    Returns habit with streak and completion statistics.
    """

    id: int = Field(..., description="Unique habit identifier", examples=[1, 42])
    name: str = Field(..., description="Habit name", examples=["Morning meditation"])
    description: str | None = Field(..., description="Habit description or null")
    frequency: HabitFrequency = Field(
        ..., description="Habit frequency", examples=[HabitFrequency.DAILY]
    )
    target_count: int = Field(
        ..., description="Target completions per period", examples=[1]
    )
    streak_count: int = Field(
        ..., description="Current consecutive day streak", examples=[7, 30], ge=0
    )
    total_completions: int = Field(
        ..., description="All-time total completions", examples=[100, 365], ge=0
    )
    created_at: datetime = Field(
        ..., description="When the habit was created", examples=["2024-01-01T00:00:00Z"]
    )
    updated_at: datetime = Field(
        ...,
        description="When the habit was last updated",
        examples=["2024-01-15T09:00:00Z"],
    )


class HabitCompletionCreate(BaseModel):
    """Schema for logging a habit completion.

    Record that a habit was completed at a specific time.
    """

    habit_id: int = Field(
        ..., description="ID of the habit being completed", examples=[1, 42]
    )
    completed_at: datetime | None = Field(
        None,
        description="When the habit was completed (defaults to now)",
        examples=["2024-01-15T09:00:00Z"],
    )
    notes: str | None = Field(
        None,
        description="Optional notes about this completion",
        examples=["Felt great!", "Difficult but worth it"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "habit_id": 1,
                    "completed_at": "2024-01-15T09:00:00Z",
                    "notes": "Felt great!",
                }
            ]
        }
    }


class HabitCompletionResponse(BaseModel):
    """Schema for habit completion response."""

    id: int = Field(..., description="Completion record ID", examples=[1001])
    habit_id: int = Field(
        ..., description="ID of the habit that was completed", examples=[1]
    )
    completed_at: datetime = Field(
        ...,
        description="When the habit was completed",
        examples=["2024-01-15T09:00:00Z"],
    )
    notes: str | None = Field(..., description="Completion notes or null")


class StreakData(BaseModel):
    """Schema for streak statistics.

    Track motivation through consecutive completion data.
    """

    current_streak: int = Field(
        ..., description="Current consecutive day streak", examples=[7, 30], ge=0
    )
    longest_streak: int = Field(
        ..., description="Longest streak ever achieved", examples=[30, 60, 100], ge=0
    )
    last_completion_date: datetime | None = Field(
        None,
        description="Date of most recent completion",
        examples=["2024-01-15T00:00:00Z"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "current_streak": 7,
                    "longest_streak": 30,
                    "last_completion_date": "2024-01-15T00:00:00Z",
                }
            ]
        }
    }


class HabitDetailResponse(HabitResponse):
    """Schema for habit detail with full completion history.

    Extended response including recent completions and streak data.
    """

    completions: list[HabitCompletionResponse] = Field(
        default_factory=list, description="Recent completion history (chronological)"
    )
    streak_data: StreakData = Field(
        ..., description="Current and best streak information"
    )


class TimeSeriesData(BaseModel):
    """Schema for time-series aggregated completion data.

    Used for charts and analytics visualization.
    """

    date: str = Field(
        ..., description="Date in YYYY-MM-DD format", examples=["2024-01-15"]
    )
    count: int = Field(
        ..., description="Number of completions on this date", examples=[3], ge=0
    )


class HabitListResponse(BaseModel):
    """Schema for habit list response."""

    habits: list[HabitResponse] = Field(
        default_factory=list, description="List of habits (may be empty)"
    )
    total: int = Field(..., description="Total count of habits", examples=[10])


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str = Field(
        ..., description="Error type", examples=["ValidationError", "NotFound"]
    )
    message: str = Field(
        ...,
        description="Human-readable error message",
        examples=["Habit not found", "Invalid frequency"],
    )
    detail: str | None = Field(None, description="Additional technical details")

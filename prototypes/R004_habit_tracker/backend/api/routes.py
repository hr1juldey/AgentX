# =============================================================================
# R004 Habit Tracker - API Routes
# =============================================================================
# FastAPI routes for Habit Tracker CRUD operations
# =============================================================================

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from models.schemas import (
    HabitCompletionCreate,
    HabitCompletionResponse,
    HabitCreate,
    HabitDetailResponse,
    HabitListResponse,
    HabitResponse,
    StreakData,
    TimeSeriesData,
)
from services.service import get_habit_service

router = APIRouter(prefix="/habits", tags=["habits"])

# Service instance
habit_service = get_habit_service()


# -----------------------------------------------------------------------------
# Habit Endpoints
# -----------------------------------------------------------------------------
@router.post("", response_model=HabitResponse, status_code=201)
async def create_habit(habit: HabitCreate) -> HabitResponse:
    """Create a new habit.

    Args:
        habit: Habit creation data

    Returns:
        Created habit with ID and timestamps

    """
    return await habit_service.create_habit(habit)


@router.get("", response_model=HabitListResponse)
async def list_habits() -> HabitListResponse:
    """List all habits.

    Returns:
        Dictionary with habits list and total count

    """
    habits = await habit_service.list_habits()
    return HabitListResponse(habits=habits, total=len(habits))


@router.get("/{habit_id}", response_model=HabitDetailResponse)
async def get_habit(habit_id: int) -> HabitDetailResponse:
    """Get a habit by ID with completion history.

    Args:
        habit_id: Habit ID

    Returns:
        Habit detail with completions and streak data

    Raises:
        HTTPException: If habit not found (404)

    """
    result = await habit_service.get_habit_detail(habit_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    return result


@router.delete("/{habit_id}", status_code=204)
async def delete_habit(habit_id: int) -> None:
    """Delete a habit by ID.

    Args:
        habit_id: Habit ID

    Raises:
        HTTPException: If habit not found (404)

    """
    success = await habit_service.delete_habit(habit_id)
    if not success:
        raise HTTPException(status_code=404, detail="Habit not found")


# -----------------------------------------------------------------------------
# Completion Endpoints
# -----------------------------------------------------------------------------
@router.post("/{habit_id}/completions", response_model=HabitCompletionResponse, status_code=201)
async def record_completion(
    habit_id: int, completion: HabitCompletionCreate
) -> HabitCompletionResponse:
    """Record a habit completion.

    Args:
        habit_id: Habit ID (URL parameter)
        completion: Completion data (habit_id in body must match URL parameter)

    Returns:
        Created completion record

    Raises:
        HTTPException: If habit not found (404)

    """
    # Ensure habit_id matches
    completion.habit_id = habit_id

    try:
        return await habit_service.record_completion(completion)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{habit_id}/completions", response_model=list[HabitCompletionResponse])
async def get_completions(habit_id: int) -> list[HabitCompletionResponse]:
    """Get all completions for a habit.

    Args:
        habit_id: Habit ID

    Returns:
        List of completions sorted by completion time (newest first)

    Raises:
        HTTPException: If habit not found (404)

    """
    habit = await habit_service.get_habit(habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")

    return await habit_service.get_habit_completions(habit_id)


# -----------------------------------------------------------------------------
# Streak Endpoints
# -----------------------------------------------------------------------------
@router.get("/{habit_id}/streak", response_model=StreakData)
async def get_streak(habit_id: int) -> StreakData:
    """Get streak data for a habit.

    Args:
        habit_id: Habit ID

    Returns:
        Streak data including current and longest streaks

    Raises:
        HTTPException: If habit not found (404)

    """
    habit = await habit_service.get_habit(habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")

    return await habit_service.get_streak_data(habit_id)


# -----------------------------------------------------------------------------
# Time-Series Endpoints
# -----------------------------------------------------------------------------
@router.get("/{habit_id}/timeseries", response_model=list[TimeSeriesData])
async def get_time_series(
    habit_id: int,
    days: Annotated[int, Query(ge=1, le=365, description="Number of days to include")] = 30,
) -> list[TimeSeriesData]:
    """Get time-series completion data for a habit.

    Args:
        habit_id: Habit ID
        days: Number of days to include (default: 30, max: 365)

    Returns:
        List of daily completion counts

    Raises:
        HTTPException: If habit not found (404)

    """
    habit = await habit_service.get_habit(habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")

    return await habit_service.get_time_series_data(habit_id, days)

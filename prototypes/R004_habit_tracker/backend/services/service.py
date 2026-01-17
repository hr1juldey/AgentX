# =============================================================================
# R004 Habit Tracker - Service Layer
# =============================================================================
# Business logic for habit tracking with streak calculation and time-series aggregation
# =============================================================================

from collections import defaultdict
from datetime import UTC, date, datetime, timedelta

from models.schemas import (
    HabitCompletionCreate,
    HabitCompletionResponse,
    HabitCreate,
    HabitDetailResponse,
    HabitResponse,
    StreakData,
    TimeSeriesData,
)


class HabitService:
    """Service for managing habits and tracking completions with streaks."""

    def __init__(self) -> None:
        """Initialize the service with empty storage."""
        self._habits: dict[int, HabitResponse] = {}
        self._completions: dict[int, list[HabitCompletionResponse]] = defaultdict(list)
        self._next_habit_id = 1
        self._next_completion_id = 1

    async def create_habit(self, habit: HabitCreate) -> HabitResponse:
        """Create a new habit.

        Args:
            habit: Habit creation data

        Returns:
            Created habit with ID and timestamps

        """
        now = datetime.now(UTC)

        habit_response = HabitResponse(
            id=self._next_habit_id,
            name=habit.name,
            description=habit.description,
            frequency=habit.frequency,
            target_count=habit.target_count,
            streak_count=0,
            total_completions=0,
            created_at=now,
            updated_at=now,
        )
        self._habits[self._next_habit_id] = habit_response
        self._next_habit_id += 1
        return habit_response

    async def get_habit(self, habit_id: int) -> HabitResponse | None:
        """Get a habit by ID.

        Args:
            habit_id: Habit ID

        Returns:
            Habit if found, None otherwise

        """
        return self._habits.get(habit_id)

    async def list_habits(self) -> list[HabitResponse]:
        """List all habits.

        Returns:
            List of all habits sorted by creation date (newest first)

        """
        habits = list(self._habits.values())
        return sorted(habits, key=lambda h: h.created_at, reverse=True)

    async def delete_habit(self, habit_id: int) -> bool:
        """Delete a habit by ID.

        Args:
            habit_id: Habit ID

        Returns:
            True if deleted, False if not found

        """
        if habit_id not in self._habits:
            return False

        del self._habits[habit_id]
        # Also delete associated completions
        if habit_id in self._completions:
            del self._completions[habit_id]
        return True

    async def record_completion(self, completion: HabitCompletionCreate) -> HabitCompletionResponse:
        """Record a habit completion.

        Args:
            completion: Completion creation data

        Returns:
            Created completion record

        Raises:
            ValueError: If habit not found

        """
        habit = self._habits.get(completion.habit_id)
        if habit is None:
            raise ValueError(f"Habit {completion.habit_id} not found")

        # Default to now if no completion time provided
        completed_at = completion.completed_at if completion.completed_at else datetime.now(UTC)

        completion_response = HabitCompletionResponse(
            id=self._next_completion_id,
            habit_id=completion.habit_id,
            completed_at=completed_at,
            notes=completion.notes,
        )
        self._completions[completion.habit_id].append(completion_response)
        self._next_completion_id += 1

        # Update habit stats
        habit.total_completions += 1
        habit.streak_count = await self._calculate_current_streak(completion.habit_id)
        habit.updated_at = datetime.now(UTC)

        return completion_response

    async def get_habit_completions(self, habit_id: int) -> list[HabitCompletionResponse]:
        """Get all completions for a habit.

        Args:
            habit_id: Habit ID

        Returns:
            List of completions sorted by completion time (newest first)

        """
        completions = self._completions.get(habit_id, [])
        return sorted(completions, key=lambda c: c.completed_at, reverse=True)

    async def get_streak_data(self, habit_id: int) -> StreakData:
        """Get detailed streak data for a habit.

        Args:
            habit_id: Habit ID

        Returns:
            Streak data including current and longest streaks

        """
        completions = self._completions.get(habit_id, [])
        if not completions:
            return StreakData(current_streak=0, longest_streak=0, last_completion_date=None)

        # Sort by completion date (oldest first for streak calculation)
        sorted_completions = sorted(completions, key=lambda c: c.completed_at)

        current_streak = await self._calculate_current_streak(habit_id)
        longest_streak = await self._calculate_longest_streak(habit_id)
        last_completion_date = sorted_completions[-1].completed_at

        return StreakData(
            current_streak=current_streak,
            longest_streak=longest_streak,
            last_completion_date=last_completion_date,
        )

    async def get_habit_detail(self, habit_id: int) -> HabitDetailResponse | None:
        """Get habit with completion history and streak data.

        Args:
            habit_id: Habit ID

        Returns:
            Habit detail if found, None otherwise

        """
        habit = self._habits.get(habit_id)
        if habit is None:
            return None

        completions = await self.get_habit_completions(habit_id)
        streak_data = await self.get_streak_data(habit_id)

        return HabitDetailResponse(
            id=habit.id,
            name=habit.name,
            description=habit.description,
            frequency=habit.frequency,
            target_count=habit.target_count,
            streak_count=habit.streak_count,
            total_completions=habit.total_completions,
            created_at=habit.created_at,
            updated_at=habit.updated_at,
            completions=completions,
            streak_data=streak_data,
        )

    async def get_time_series_data(self, habit_id: int, days: int = 30) -> list[TimeSeriesData]:
        """Get time-series aggregated completion data.

        Args:
            habit_id: Habit ID
            days: Number of days to include (default: 30)

        Returns:
            List of daily completion counts

        """
        completions = self._completions.get(habit_id, [])
        if not completions:
            return []

        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)

        # Group completions by date
        daily_counts: dict[date, int] = defaultdict(int)
        for completion in completions:
            completion_date = completion.completed_at.date()
            if start_date <= completion_date <= end_date:
                daily_counts[completion_date] += 1

        # Fill in missing dates with 0
        time_series = []
        current_date = start_date
        while current_date <= end_date:
            count = daily_counts.get(current_date, 0)
            time_series.append(TimeSeriesData(date=current_date.isoformat(), count=count))
            current_date += timedelta(days=1)

        return time_series

    async def _calculate_current_streak(self, habit_id: int) -> int:
        """Calculate the current streak for a habit.

        A streak is the number of consecutive days (for daily habits) or
        weeks (for weekly habits) with at least one completion.

        The streak is broken if there's a gap longer than the frequency period.

        Args:
            habit_id: Habit ID

        Returns:
            Current streak count

        """
        habit = self._habits.get(habit_id)
        if habit is None:
            return 0

        completions = self._completions.get(habit_id, [])
        if not completions:
            return 0

        # Sort by completion date (most recent first)
        sorted_completions = sorted(completions, key=lambda c: c.completed_at, reverse=True)

        # Determine the period based on frequency
        period_days = 1 if habit.frequency == "daily" else 7

        streak = 0
        current_date = date.today()

        # Check each period going backwards
        for completion in sorted_completions:
            completion_date = completion.completed_at.date()
            days_diff = (current_date - completion_date).days

            # If completion is within the current period
            if days_diff < period_days:
                # Haven't counted this period yet
                if streak == 0 or (current_date - completion_date).days >= 0:
                    streak += 1
                    # Move to previous period
                    current_date = completion_date - timedelta(days=period_days)
            else:
                # Gap found, streak broken
                break

        return streak

    async def _calculate_longest_streak(self, habit_id: int) -> int:
        """Calculate the longest streak in history for a habit.

        Args:
            habit_id: Habit ID

        Returns:
            Longest streak count

        """
        habit = self._habits.get(habit_id)
        if habit is None:
            return 0

        completions = self._completions.get(habit_id, [])
        if not completions:
            return 0

        # Sort by completion date (oldest first)
        sorted_completions = sorted(completions, key=lambda c: c.completed_at)

        # Determine the period based on frequency
        period_days = 1 if habit.frequency == "daily" else 7

        longest_streak = 0
        current_streak = 0
        last_period_date: date | None = None

        for completion in sorted_completions:
            completion_date = completion.completed_at.date()

            if last_period_date is None:
                # First completion
                current_streak = 1
                last_period_date = completion_date
            else:
                # Calculate which period this completion falls into
                days_diff = (completion_date - last_period_date).days

                if days_diff < period_days:
                    # Same period as last completion, don't double count
                    continue
                elif days_diff <= period_days * 2:
                    # Next consecutive period
                    current_streak += 1
                    last_period_date = completion_date
                else:
                    # Gap found, reset streak
                    longest_streak = max(longest_streak, current_streak)
                    current_streak = 1
                    last_period_date = completion_date

        longest_streak = max(longest_streak, current_streak)
        return longest_streak


# Singleton instance
_habit_service: HabitService | None = None


def get_habit_service() -> HabitService:
    """Get the singleton Habit service instance."""
    global _habit_service
    if _habit_service is None:
        _habit_service = HabitService()
    return _habit_service

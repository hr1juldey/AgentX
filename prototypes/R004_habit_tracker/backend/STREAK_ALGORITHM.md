# Streak Calculation Algorithm

## Overview

The Habit Tracker implements a sophisticated streak calculation system that tracks both **current streaks** (active consecutive periods) and **longest streaks** (best performance all-time). The algorithm supports both daily and weekly habit frequencies.

## Key Concepts

### Period

A **period** is the time unit for which a habit needs to be completed:
- **Daily habits**: 1 day
- **Weekly habits**: 7 days

### Completion

A **completion** records when a habit was done. Multiple completions in the same period still count as one for streak purposes.

### Streak

A **streak** is the count of consecutive periods with at least one completion.

## Algorithm Details

### Current Streak Calculation

```python
async def _calculate_current_streak(self, habit_id: int) -> int:
```

**Steps:**

1. **Get completions**: Retrieve all completions for the habit
2. **Sort by date**: Most recent first (descending order)
3. **Determine period**: Set period_days based on frequency (1=daily, 7=weekly)
4. **Initialize**: Set current_date = today, streak = 0
5. **Iterate backwards**:
   - For each completion, calculate days_diff = (current_date - completion_date).days
   - If days_diff < period_days: The completion is in the current period
     - If we haven't counted this period yet (streak == 0 or moved to new period)
       - Increment streak
       - Move current_date back by period_days
   - If days_diff >= period_days * 2: Gap found, streak broken
     - Break the loop
6. **Return streak**

**Example (Daily Habit):**

```
Today: Jan 16
Completions: [Jan 16, Jan 15, Jan 14, Jan 12, Jan 11]

Calculation:
- Jan 16: days_diff=0 < 1 → streak=1, current_date=Jan 15
- Jan 15: days_diff=0 < 1 → streak=2, current_date=Jan 14
- Jan 14: days_diff=0 < 1 → streak=3, current_date=Jan 13
- Jan 12: days_diff=1 (not < 1) → Check if in next period
  - (Jan 13 - Jan 12) = 1 day → Gap found (missed Jan 13)
  - Break
Result: Current streak = 3 days (Jan 14-16)
```

### Longest Streak Calculation

```python
async def _calculate_longest_streak(self, habit_id: int) -> int:
```

**Steps:**

1. **Get completions**: Retrieve all completions for the habit
2. **Sort by date**: Oldest first (ascending order)
3. **Determine period**: Set period_days based on frequency
4. **Initialize**: longest_streak=0, current_streak=0, last_period_date=None
5. **Iterate forward**:
   - For each completion, get completion_date
   - If first completion:
     - current_streak = 1
     - last_period_date = completion_date
   - Else:
     - Calculate days_diff = (completion_date - last_period_date).days
     - If days_diff < period_days: Same period, skip (don't double count)
     - If days_diff <= period_days * 2: Next consecutive period
       - current_streak += 1
       - last_period_date = completion_date
     - If days_diff > period_days * 2: Gap found
       - longest_streak = max(longest_streak, current_streak)
       - Reset: current_streak = 1, last_period_date = completion_date
6. **Final update**: longest_streak = max(longest_streak, current_streak)
7. **Return longest_streak**

**Example (Daily Habit):**

```
Completions: [Jan 1, Jan 2, Jan 3, Jan 5, Jan 6, Jan 10]

Calculation:
- Jan 1: First completion → current_streak=1, last=Jan 1
- Jan 2: days_diff=1 ≤ 2 → Next period → current_streak=2, last=Jan 2
- Jan 3: days_diff=1 ≤ 2 → Next period → current_streak=3, last=Jan 3
- Jan 5: days_diff=2 ≤ 2 → Next period → current_streak=4, last=Jan 5
- Jan 6: days_diff=1 ≤ 2 → Next period → current_streak=5, last=Jan 6
- Jan 10: days_diff=4 > 2 → Gap!
  - longest_streak = max(0, 5) = 5
  - Reset: current_streak=1, last=Jan 10
Final: longest_streak = max(5, 1) = 5
Result: Longest streak = 5 days (Jan 1-6, with Jan 4 missed but within range)
```

## Time-Series Aggregation

```python
async def get_time_series_data(self, habit_id: int, days: int = 30)
```

**Steps:**

1. **Calculate range**: end_date = today, start_date = today - (days - 1)
2. **Group by date**: Count completions per date
3. **Fill gaps**: Add missing dates with count=0
4. **Return array**: List of {date, count} objects

**Example Output:**

```json
[
  {"date": "2025-12-18", "count": 1},
  {"date": "2025-12-19", "count": 0},
  {"date": "2025-12-20", "count": 2},
  ...
  {"date": "2026-01-16", "count": 1}
]
```

## Edge Cases Handled

1. **No completions**: Returns streak=0, last_completion_date=None
2. **Multiple completions per period**: Counts as one for streak
3. **Completions in future**: Handled by datetime.now(UTC) defaults
4. **Gap exactly at threshold**: If days_diff == period_days * 2, counts as consecutive
5. **Weekly habits**: All calculations use 7-day periods instead of 1-day

## Data Structures

### In-Memory Storage

```python
self._habits: dict[int, HabitResponse] = {}
self._completions: dict[int, list[HabitCompletionResponse]] = defaultdict(list)
```

### Completion Record

```python
HabitCompletionResponse:
  id: int
  habit_id: int
  completed_at: datetime
  notes: str | None
```

### Streak Data

```python
StreakData:
  current_streak: int
  longest_streak: int
  last_completion_date: datetime | None
```

## Performance Considerations

- **Time Complexity**: O(n log n) due to sorting, where n = number of completions
- **Space Complexity**: O(n) for storing completion history
- **Optimization**: For production with many completions, consider:
  - Date-based indexing
  - Caching streak calculations
  - Lazy evaluation of time-series data

## Testing

The algorithm is tested in `tests/test_api.py`:

- `test_get_streak_new_habit` - Empty state
- `test_get_streak_with_completions` - With data
- `test_get_timeseries_with_completions` - Aggregation
- Various edge cases for validation

## Future Enhancements

1. **Timezone support**: Currently uses UTC, could add user timezone
2. **Custom periods**: Support custom frequency (e.g., every 3 days)
3. **Streak freezing**: Allow "pausing" streaks for vacations
4. **Predictive streaks**: Calculate when streak will break
5. **Persistence**: Move from in-memory to database storage

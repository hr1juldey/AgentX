# R004 Habit Tracker Backend - Quick Start Guide

## Files Created

### Core Application Files

| File | Description |
|------|-------------|
| `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R004_habit_tracker/backend/main.py` | FastAPI application entry point |
| `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R004_habit_tracker/backend/config/settings.py` | Configuration settings with Pydantic |
| `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R004_habit_tracker/backend/models/schemas.py` | Pydantic models for API validation |
| `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R004_habit_tracker/backend/services/service.py` | Business logic with streak calculation |
| `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R004_habit_tracker/backend/api/routes.py` | FastAPI route definitions |

### Configuration Files

| File | Description |
|------|-------------|
| `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R004_habit_tracker/backend/pyproject.toml` | Python project configuration |
| `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R004_habit_tracker/backend/.env.example` | Environment variables template |
| `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R004_habit_tracker/backend/.env` | Actual environment variables |
| `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R004_habit_tracker/backend/.gitignore` | Git ignore patterns |

### Scripts

| File | Description |
|------|-------------|
| `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R004_habit_tracker/backend/scripts/run.sh` | Start the development server |
| `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R004_habit_tracker/backend/scripts/test.sh` | Run tests with coverage |

### Tests

| File | Description |
|------|-------------|
| `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R004_habit_tracker/backend/tests/test_api.py` | Comprehensive API tests |

### Documentation

| File | Description |
|------|-------------|
| `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R004_habit_tracker/backend/README.md` | Main documentation |
| `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R004_habit_tracker/backend/STREAK_ALGORITHM.md` | Streak calculation algorithm details |

## Getting Started

### 1. Install Dependencies

```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R004_habit_tracker/backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 2. Run the Server

```bash
./scripts/run.sh
```

The API will be available at `http://localhost:8004`

### 3. Test the API

```bash
./scripts/test.sh
```

Or visit `http://localhost:8004/docs` for interactive API documentation.

## API Endpoints

### Habits

```bash
# Create a habit
curl -X POST http://localhost:8004/api/v1/habits \
  -H "Content-Type: application/json" \
  -d '{"name": "Exercise", "frequency": "daily", "target_count": 1}'

# List all habits
curl http://localhost:8004/api/v1/habits

# Get habit with details
curl http://localhost:8004/api/v1/habits/1

# Delete a habit
curl -X DELETE http://localhost:8004/api/v1/habits/1
```

### Completions

```bash
# Record a completion
curl -X POST http://localhost:8004/api/v1/habits/1/completions \
  -H "Content-Type: application/json" \
  -d '{"notes": "Great workout!"}'

# Get completions
curl http://localhost:8004/api/v1/habits/1/completions
```

### Streaks

```bash
# Get streak data
curl http://localhost:8004/api/v1/habits/1/streak
```

### Time-Series

```bash
# Get daily completion counts (default 30 days)
curl http://localhost:8004/api/v1/habits/1/timeseries

# Custom days
curl http://localhost:8004/api/v1/habits/1/timeseries?days=7
```

## Streak Calculation Logic

The streak calculation algorithm tracks both **current streak** and **longest streak** for habits.

### Current Streak

- Counts consecutive days/weeks with at least one completion
- Starts from today and works backwards
- Breaks when a period has no completions
- Supports both daily and weekly frequencies

### Longest Streak

- Scans all historical completions
- Tracks the maximum consecutive period streak
- Handles gaps and missed periods
- Updates automatically when new completions are recorded

### Algorithm Details

See `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R004_habit_tracker/backend/STREAK_ALGORITHM.md` for complete documentation including:

- Step-by-step algorithm explanation
- Example calculations
- Edge cases handled
- Performance considerations
- Time-series aggregation logic

## Level 2 Features

This prototype adds Level 2 complexity building on R001-R003:

1. **Time-Series Aggregation**: Daily completion counts for analytics and visualization
2. **Streak Tracking**: Sophisticated algorithm for calculating current and longest streaks
3. **Frequency Support**: Both daily and weekly habit frequencies
4. **Derived Metrics**: Streak counts, total completions, last completion date

## Key Differences from R003

| Feature | R003 Pomodoro | R004 Habit Tracker |
|---------|---------------|-------------------|
| Real-time updates | WebSocket | REST only |
| Core entity | Sessions | Habits |
| Time tracking | Countdown timer | Historical records |
| Analytics | Basic | Time-series aggregation |
| Computation | Simple countdown | Complex streak algorithm |

## Configuration

Edit `.env` to customize:

```bash
PORT=8004                    # Server port
APP_NAME=Habit Tracker       # Application name
FRONTEND_URL=http://localhost:3000  # CORS allowed origin
```

## Testing

The test suite covers:

- Health endpoints
- Habit CRUD operations
- Completion recording
- Streak calculations
- Time-series aggregation
- Edge cases and error handling

Run with: `./scripts/test.sh`

## Next Steps

1. Start the server: `./scripts/run.sh`
2. Visit `http://localhost:8004/docs` for interactive API docs
3. Create a habit and record some completions
4. Check the streak calculation in action
5. Review the streak algorithm documentation for deeper understanding

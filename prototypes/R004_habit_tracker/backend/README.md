# R004 Habit Tracker - Backend

FastAPI backend for the Habit Tracker prototype with streak tracking and time-series aggregation.

## Features

- **Habit Management**: Create, read, update, and delete habits
- **Completion Tracking**: Record when habits are completed
- **Streak Calculation**: Automatic calculation of current and longest streaks
- **Time-Series Aggregation**: Daily completion counts for analytics
- **Frequency Support**: Daily and weekly habit frequencies

## Project Structure

```
backend/
├── config/
│   └── settings.py          # Configuration settings
├── models/
│   └── schemas.py           # Pydantic models for API
├── services/
│   └── service.py           # Business logic with streak calculation
├── api/
│   └── routes.py            # FastAPI routes
├── tests/
│   └── test_api.py          # API tests
├── scripts/
│   ├── run.sh               # Start the server
│   └── test.sh              # Run tests
├── data/
│   └── .gitkeep             # Data directory
├── main.py                  # FastAPI application entry point
├── pyproject.toml           # Python project configuration
├── .env.example             # Example environment variables
└── .env                     # Actual environment variables (not in git)
```

## Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

## Running the Server

```bash
# Using the script
./scripts/run.sh

# Or directly
python -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload
```

The API will be available at:
- API: `http://localhost:8004`
- Interactive docs: `http://localhost:8004/docs`
- Alternative docs: `http://localhost:8004/redoc`

## Testing

```bash
# Using the script
./scripts/test.sh

# Or directly
python -m pytest tests/ -v
```

## API Endpoints

### Habits

- `POST /api/v1/habits` - Create a new habit
- `GET /api/v1/habits` - List all habits
- `GET /api/v1/habits/{id}` - Get habit with completion history
- `DELETE /api/v1/habits/{id}` - Delete a habit

### Completions

- `POST /api/v1/habits/{id}/completions` - Record a completion
- `GET /api/v1/habits/{id}/completions` - Get all completions

### Streaks

- `GET /api/v1/habits/{id}/streak` - Get streak data

### Time-Series

- `GET /api/v1/habits/{id}/timeseries?days=30` - Get daily completion counts

## Streak Calculation Logic

The streak calculation works as follows:

### Current Streak

1. Completions are sorted by date (most recent first)
2. Starting from today, we check backwards day by day (for daily habits)
3. A completion is counted for a period if it falls within that period
4. The streak breaks when a period has no completions

### Longest Streak

1. Completions are sorted by date (oldest first)
2. We track consecutive periods with at least one completion
3. When a gap is found, the current streak ends and a new one begins
4. The maximum streak across all time is returned

### Frequency Support

- **Daily**: Streak counts consecutive days
- **Weekly**: Streak counts consecutive weeks (7-day periods)

## Configuration

Edit `.env` to customize:

```bash
APP_NAME=Habit Tracker
PORT=8004
DEBUG=true
FRONTEND_URL=http://localhost:3000
```

## Technologies

- FastAPI - Web framework
- Pydantic - Data validation
- Uvicorn - ASGI server
- Pytest - Testing framework
- Python 3.11+

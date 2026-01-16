# R003 Pomodoro Timer - Quick Start Guide

## Server Information

- **Name**: Pomodoro Timer
- **Port**: 8003
- **WebSocket**: Supported at `/api/v1/sessions/ws/timer/{session_id}`

## Quick Start

```bash
# 1. Navigate to backend directory
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R003_pomodoro_timer/backend

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -e ".[dev]"

# 4. Run the server
./scripts/run.sh
```

Server starts at: `http://0.0.0.0:8003`

## API Endpoints

### REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/sessions` | Create session |
| GET | `/api/v1/sessions` | List sessions |
| GET | `/api/v1/sessions/{id}` | Get session |
| PUT | `/api/v1/sessions/{id}` | Update session |
| DELETE | `/api/v1/sessions/{id}` | Delete session |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `/api/v1/sessions/ws/timer/{id}` | Real-time countdown |

## Example Usage

### Create Session

```bash
curl -X POST http://localhost:8003/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"title": "Work", "work_duration": 25, "break_duration": 5}'
```

### Pause Session

```bash
curl -X PUT http://localhost:8003/api/v1/sessions/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "paused"}'
```

### WebSocket Client (JavaScript)

```javascript
const ws = new WebSocket('ws://localhost:8003/api/v1/sessions/ws/timer/1');
ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

## Testing

```bash
# Run tests
./scripts/test.sh

# Or with pytest
pytest --cov=. -v
```

## Linting

```bash
# Check code
./scripts/lint.sh

# Format code
ruff format .
```

## Session Status Values

- `running`: Timer is counting down
- `paused`: Timer is paused
- `completed`: Timer finished naturally
- `cancelled`: Timer was cancelled

## Default Durations

- Work: 25 minutes (1500 seconds)
- Break: 5 minutes (300 seconds)

# Quick Start Guide - Session Manager Backend

## Setup (2 minutes)

```bash
# Navigate to backend
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R006_session_manager/backend

# Install dependencies
pip install -e .

# Start Redis (if using Redis storage)
redis-server --daemonize yes

# Run the server
python main.py
```

Server starts at: **http://localhost:8006**

API Docs: **http://localhost:8006/docs**

## Test Redis Connection

```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# Check storage status
curl http://localhost:8006/sessions/status/storage
```

## Quick Test

```bash
# Create a session
curl -X POST http://localhost:8006/sessions \
  -H "Content-Type: application/json" \
  -H "X-User-Id: test_user_123" \
  -d '{
    "device_name": "My Laptop",
    "device_type": "desktop",
    "user_agent": "Mozilla/5.0 Test Browser",
    "ip_address": "192.168.1.100"
  }'

# List all sessions
curl http://localhost:8006/sessions \
  -H "X-User-Id: test_user_123"

# Get storage status
curl http://localhost:8006/sessions/status/storage
```

## Run Tests

```bash
# All tests
./scripts/test.sh

# Or with pytest
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=. --cov-report=html
```

## Environment Variables

Edit `.env` file:

```bash
PORT=8006                          # Server port
REDIS_URL=redis://localhost:6379/0 # Redis connection
SESSION_EXPIRY_HOURS=24            # Session lifetime
```

## Without Redis

If Redis is not running, the backend **automatically** falls back to in-memory storage with a warning:

```
⚠️  Redis connection failed: Error connecting to Redis
🔄 Falling back to in-memory storage (not recommended for production)
```

## Project Structure

```
backend/
├── api/routes.py          # REST endpoints
├── config/settings.py     # Configuration
├── models/schemas.py      # Pydantic models
├── services/service.py    # Business logic (Redis + fallback)
├── tests/test_api.py      # Test suite
├── main.py                # Entry point
└── scripts/
    ├── run.sh             # Start server
    ├── test.sh            # Run tests
    └── install.sh         # Install deps
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/sessions` | Create session (login) |
| GET | `/sessions` | List sessions |
| GET | `/sessions/{id}` | Get session |
| PUT | `/sessions/{id}` | Update session |
| DELETE | `/sessions/{id}` | Delete session |
| DELETE | `/sessions` | Delete all sessions |
| GET | `/sessions/status/storage` | Storage status |
| GET | `/health` | Health check |

All session endpoints require: `X-User-Id: user_id` header

## Next Steps

1. Start Redis: `redis-server --daemonize yes`
2. Install deps: `pip install -e .`
3. Run server: `python main.py`
4. Open docs: http://localhost:8006/docs
5. Test with curl or the Swagger UI

## Troubleshooting

**Port already in use?**
```bash
# Change port in .env
PORT=8007
```

**Redis connection refused?**
```bash
# Start Redis
redis-server --daemonize yes

# Or use in-memory fallback (automatic)
# Server will log warning and continue
```

**Tests failing?**
```bash
# Check Redis is running
redis-cli ping

# Reinstall dependencies
pip install -e . --force-reinstall
```

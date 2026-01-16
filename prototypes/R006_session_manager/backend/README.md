# Session Manager Backend

FastAPI backend for managing user sessions across multiple devices with Redis storage.

## Features

- Redis-based session storage with automatic expiry
- In-memory fallback when Redis is unavailable
- Multi-device session tracking (desktop, mobile, tablet)
- Device fingerprinting (user agent + IP address)
- Session management (create, read, update, delete)
- Per-user and global session operations
- Automatic last_active timestamp updates

## Requirements

- Python 3.11+
- Redis server (optional - falls back to in-memory storage)

## Installation

```bash
# Install dependencies
pip install -e .

# Or use the install script
./scripts/install.sh
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key settings:
- `PORT`: Server port (default: 8006)
- `REDIS_URL`: Redis connection string (default: redis://localhost:6379/0)
- `SESSION_EXPIRY_HOURS`: Session lifetime in hours (default: 24)

## Running

```bash
# Run the server
python main.py

# Or use the run script
./scripts/run.sh
```

Server will be available at `http://localhost:8006`

API documentation: `http://localhost:8006/docs`

## API Endpoints

### Sessions

- `POST /sessions` - Create a new session (login)
- `GET /sessions` - List all sessions for authenticated user
- `GET /sessions/{id}` - Get session details
- `PUT /sessions/{id}` - Update session status
- `DELETE /sessions/{id}` - Delete a session (logout)
- `DELETE /sessions` - Delete all sessions (logout all devices)

### Health

- `GET /` - Root endpoint with service info
- `GET /health` - Health check with storage status
- `GET /sessions/status/storage` - Storage backend status

## Authentication

All session endpoints require `X-User-Id` header:

```
X-User-Id: user_1234567890
```

In production, this would be a JWT token.

## Testing

```bash
# Run tests
pytest tests/ -v

# Or use the test script
./scripts/test.sh
```

## Redis vs In-Memory Storage

The service automatically detects Redis availability:

- **Redis**: Recommended for production. Handles session expiry automatically.
- **In-Memory Fallback**: Activated when Redis is unavailable. Not recommended for production as sessions are lost on restart.

Check storage status:

```bash
curl http://localhost:8006/sessions/status/storage
```

## Example Usage

### Create a Session

```bash
curl -X POST http://localhost:8006/sessions \
  -H "Content-Type: application/json" \
  -H "X-User-Id: user_123" \
  -d '{
    "device_name": "My Desktop",
    "device_type": "desktop",
    "user_agent": "Mozilla/5.0...",
    "ip_address": "192.168.1.100"
  }'
```

### List Sessions

```bash
curl http://localhost:8006/sessions \
  -H "X-User-Id: user_123"
```

### Delete a Session

```bash
curl -X DELETE http://localhost:8006/sessions/{session_id} \
  -H "X-User-Id: user_123"
```

### Logout All Devices

```bash
curl -X DELETE http://localhost:8006/sessions \
  -H "X-User-Id: user_123"
```

## Project Structure

```
backend/
├── config/
│   ├── __init__.py
│   └── settings.py          # Application configuration
├── models/
│   ├── __init__.py
│   └── schemas.py           # Pydantic models
├── services/
│   ├── __init__.py
│   └── service.py           # Business logic (Redis + fallback)
├── api/
│   ├── __init__.py
│   └── routes.py            # API endpoints
├── tests/
│   ├── __init__.py
│   └── test_api.py          # API tests
├── scripts/
│   ├── run.sh               # Start server
│   ├── test.sh              # Run tests
│   └── install.sh           # Install dependencies
├── data/
│   └── .gitkeep             # Data directory
├── main.py                  # Application entry point
├── pyproject.toml           # Project config
├── .env.example             # Environment template
└── .gitignore               # Git ignore rules
```

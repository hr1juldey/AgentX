# R002 Todo List - Backend API

FastAPI backend for the Todo List prototype (Level 1: Basic CRUD with due dates).

## Features

- Full CRUD operations for todos
- Todo attributes: title, description, due_date, priority, status
- Filtering by status (todo, in_progress, done)
- Filtering by priority (low, medium, high)
- In-memory storage (same pattern as R001)
- RESTful API design
- Comprehensive test coverage

## Quick Start

### Installation

```bash
# Create virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .

# Or using uv (faster)
uv venv
source .venv/bin/activate
uv pip install -e .
```

### Running the Server

```bash
# Using the run script
./scripts/run.sh

# Or directly
python main.py
```

The server will start on `http://localhost:8002`

### API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8002/docs`
- ReDoc: `http://localhost:8002/redoc`

## API Endpoints

### Todos

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/todos` | Create a new todo |
| GET | `/api/v1/todos` | List all todos (with optional filters) |
| GET | `/api/v1/todos/{id}` | Get a specific todo |
| PUT | `/api/v1/todos/{id}` | Update a todo |
| DELETE | `/api/v1/todos/{id}` | Delete a todo |

### Query Parameters

**List Todos (`GET /api/v1/todos`):**
- `status`: Filter by status (`todo`, `in_progress`, `done`)
- `priority`: Filter by priority (`low`, `medium`, `high`)
- `limit`: Max results to return (default: 50, max: 100)

### Example Requests

```bash
# Create a todo
curl -X POST http://localhost:8002/api/v1/todos \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Build prototype",
    "description": "Create the Todo List prototype",
    "due_date": "2026-01-20T10:00:00Z",
    "priority": "high",
    "status": "in_progress"
  }'

# List all todos
curl http://localhost:8002/api/v1/todos

# Filter by status
curl "http://localhost:8002/api/v1/todos?status=todo"

# Filter by priority
curl "http://localhost:8002/api/v1/todos?priority=high"

# Update a todo
curl -X PUT http://localhost:8002/api/v1/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'

# Delete a todo
curl -X DELETE http://localhost:8002/api/v1/todos/1
```

## Data Models

### TodoCreate
```json
{
  "title": "string (required, 1-200 chars)",
  "description": "string (optional, max 1000 chars)",
  "due_date": "ISO 8601 datetime (optional)",
  "priority": "low|medium|high (default: medium)",
  "status": "todo|in_progress|done (default: todo)"
}
```

### TodoResponse
```json
{
  "id": "integer",
  "title": "string",
  "description": "string|null",
  "due_date": "ISO 8601 datetime|null",
  "priority": "low|medium|high",
  "status": "todo|in_progress|done",
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime"
}
```

## Testing

```bash
# Run all tests
./scripts/test.sh

# Or directly
pytest

# With coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/test_api.py::test_create_todo
```

## Development

### Project Structure

```
backend/
├── config/
│   └── settings.py       # Configuration with Pydantic Settings
├── models/
│   └── schemas.py        # Pydantic models for requests/responses
├── services/
│   └── service.py        # Business logic (in-memory storage)
├── api/
│   └── routes.py         # FastAPI route handlers
├── tests/
│   └── test_api.py       # API tests
├── scripts/
│   ├── run.sh           # Start the server
│   ├── test.sh          # Run tests
│   └── lint.sh          # Run linter
├── data/
│   └── .gitkeep         # Data directory (for future DB)
├── main.py              # FastAPI application entry point
├── pyproject.toml       # Python project configuration
├── .env.example         # Environment template
└── .env                 # Local environment (not in git)
```

### Linting

```bash
# Check code style
./scripts/lint.sh

# Or directly
ruff check .
ruff format --check .

# Auto-fix issues
ruff check --fix .
ruff format .
```

## Configuration

Configuration is managed through environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `Todo List` | Application name |
| `APP_VERSION` | `0.1.0` | Application version |
| `DEBUG` | `true` | Debug mode |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8002` | Server port |
| `FRONTEND_URL` | `http://localhost:3000` | CORS allowed origin |

## Design Patterns

This backend follows the same patterns as R001 Personal Notes:

1. **Service Layer Pattern**: Business logic isolated in `services/service.py`
2. **Singleton Service**: Global service instance for in-memory storage
3. **Pydantic Schemas**: Separate models for Create, Update, Response
4. **Async Operations**: All service methods are async
5. **HTTP Status Codes**: Proper use of 201, 204, 404, 422
6. **CORS Middleware**: Configured for frontend integration

## Next Steps

### Level 2 Enhancements
- Add tags to todos (many-to-many relationship)
- Add search functionality
- Add sorting options
- Persistent storage (SQLite)

### Level 3 Enhancements
- User authentication
- User-specific todo lists
- Categories/projects
- Collaborative sharing

### Level 4 Enhancements
- AI-powered todo suggestions
- Smart prioritization
- Natural language processing
- Due date recommendations

## Notes

- Data is stored in-memory and will be lost on server restart
- This is intentional for rapid prototyping
- Upgrade to persistent storage when ready for Level 2
- Port 8002 is used to avoid conflicts with R001 (8001)

# R002 Todo List Backend - Quick Start

## Setup (5 minutes)

### 1. Install Dependencies

```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R002_todo_list/backend

# Using uv (recommended - faster)
uv venv
source .venv/bin/activate
uv pip install -e .

# OR using standard pip
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2. Run the Server

```bash
./scripts/run.sh
```

Server will start on `http://localhost:8002`

### 3. Test the API

```bash
# Create a todo
curl -X POST http://localhost:8002/api/v1/todos \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test todo",
    "description": "This is a test",
    "priority": "high",
    "status": "todo"
  }'

# List all todos
curl http://localhost:8002/api/v1/todos

# Get specific todo
curl http://localhost:8002/api/v1/todos/1

# Update todo
curl -X PUT http://localhost:8002/api/v1/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'

# Delete todo
curl -X DELETE http://localhost:8002/api/v1/todos/1
```

### 4. Run Tests

```bash
./scripts/test.sh
```

### 5. View API Documentation

Open in browser:
- Swagger UI: http://localhost:8002/docs
- ReDoc: http://localhost:8002/redoc

## Key Differences from R001

1. **Priority enum**: `low`, `medium`, `high` (default: `medium`)
2. **Status enum**: `todo`, `in_progress`, `done` (default: `todo`)
3. **Due date**: Optional ISO 8601 datetime
4. **Filtering**: Can filter by status and priority
5. **Port**: 8002 (R001 uses 8001)

## File Locations

- Main app: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R002_todo_list/backend/main.py`
- Routes: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R002_todo_list/backend/api/routes.py`
- Schemas: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R002_todo_list/backend/models/schemas.py`
- Service: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R002_todo_list/backend/services/service.py`
- Tests: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R002_todo_list/backend/tests/test_api.py`

## Troubleshooting

**Port already in use?**
Change `PORT` in `.env` file

**Import errors?**
Make sure virtual environment is activated and dependencies installed

**Tests failing?**
Check that FastAPI is installed: `pip list | grep fastapi`

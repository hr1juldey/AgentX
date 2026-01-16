# R002 Todo List

A Kanban-style todo management application built with FastAPI and Next.js.

## Features

- **Kanban Board**: 3-column layout (Todo, In Progress, Done)
- **Priority Tracking**: Low, Medium, High with color-coded badges
- **Due Dates**: Track when tasks are due
- **Quick Actions**: Move tasks between columns with one click
- **Full CRUD**: Create, read, update, delete todos
- **Filtering**: Filter by status and priority

## Tech Stack

### Backend
- FastAPI 0.115+
- Python 3.12+
- Pydantic v2 for validation
- In-memory storage

### Frontend
- Next.js 15
- React 19
- TypeScript 5.7
- Tailwind CSS 3.4
- shadcn/ui components

## Quick Start

### Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Run development server
python main.py
# or
./scripts/run.sh
```

Backend runs on **http://localhost:8002**

API docs: **http://localhost:8002/docs**

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
# or
./scripts/dev.sh
```

Frontend runs on **http://localhost:3000**

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/todos` | Create new todo |
| GET | `/api/v1/todos` | List all todos (with filters) |
| GET | `/api/v1/todos/{id}` | Get single todo |
| PUT | `/api/v1/todos/{id}` | Update todo |
| DELETE | `/api/v1/todos/{id}` | Delete todo |

### Query Parameters

- `?status=todo` - Filter by status (todo, in_progress, done)
- `?priority=high` - Filter by priority (low, medium, high)
- `?limit=50` - Limit results (1-100, default: 50)

## Usage Examples

### Create a Todo

```bash
curl -X POST http://localhost:8002/api/v1/todos \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Build AGENTX prototype",
    "description": "Create R002 Todo List",
    "priority": "high",
    "due_date": "2025-01-20T10:00:00Z"
  }'
```

### List Todos

```bash
# All todos
curl http://localhost:8002/api/v1/todos

# Filter by status
curl "http://localhost:8002/api/v1/todos?status=todo"

# Filter by priority
curl "http://localhost:8002/api/v1/todos?priority=high"
```

### Update Todo Status

```bash
curl -X PUT http://localhost:8002/api/v1/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'
```

## Testing

### Backend Tests

```bash
cd backend
./scripts/test.sh
# or
pytest tests/
```

### Frontend Linting

```bash
cd frontend
npm run lint
# or
./scripts/lint.sh
```

## Project Structure

```
R002_todo_list/
├── backend/                 # FastAPI backend
│   ├── api/                # Route handlers
│   ├── config/             # Configuration
│   ├── models/             # Pydantic schemas
│   ├── services/           # Business logic
│   ├── tests/              # pytest tests
│   └── scripts/            # Run scripts
├── frontend/               # Next.js frontend
│   ├── app/               # Next.js 15 app directory
│   ├── components/        # React components
│   │   └── ui/           # shadcn/ui components
│   ├── lib/              # Utilities
│   └── scripts/          # Build scripts
├── PRD.md                 # Product requirements
├── README.md              # This file
└── REPORTCARD.md          # Build reportcard
```

## License

MIT

## Status

Level 1 Prototype - Complete

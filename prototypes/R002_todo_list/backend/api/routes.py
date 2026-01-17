# =============================================================================
# R002 Todo List - API Routes
# =============================================================================
# FastAPI routes for todo CRUD operations
# =============================================================================

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from models.schemas import Priority, Status, TodoCreate, TodoResponse, TodoUpdate
from services.service import get_todo_service

router = APIRouter(prefix="/todos", tags=["todos"])

# Service instance
todo_service = get_todo_service()


# -----------------------------------------------------------------------------
# Todo Endpoints
# -----------------------------------------------------------------------------
@router.post("", response_model=TodoResponse, status_code=201)
async def create_todo(todo: TodoCreate) -> TodoResponse:
    """Create a new todo.

    Args:
        todo: Todo creation data

    Returns:
        Created todo with ID and timestamps

    """
    return await todo_service.create(todo)


@router.get("", response_model=dict)
async def list_todos(
    status: Annotated[Status | None, Query(description="Filter by status")] = None,
    priority: Annotated[
        Priority | None, Query(description="Filter by priority")
    ] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> dict[str, object]:
    """List all todos with optional filtering.

    Args:
        status: Filter by status (todo, in_progress, done)
        priority: Filter by priority (low, medium, high)
        limit: Maximum number of todos to return (default: 50)

    Returns:
        Dictionary with todos list and total count

    """
    todos = await todo_service.list_all(status=status, priority=priority)
    return {
        "todos": todos[:limit],
        "total": len(todos),
    }


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: int) -> TodoResponse:
    """Get a todo by ID.

    Args:
        todo_id: Todo ID

    Returns:
        Todo data

    Raises:
        HTTPException: If todo not found (404)

    """
    result = await todo_service.get(todo_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return result


@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: int, todo_update: TodoUpdate) -> TodoResponse:
    """Update an existing todo.

    Args:
        todo_id: Todo ID
        todo_update: Todo update data (all fields optional)

    Returns:
        Updated todo

    Raises:
        HTTPException: If todo not found (404)

    """
    result = await todo_service.update(todo_id, todo_update)
    if result is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return result


@router.delete("/{todo_id}", status_code=204)
async def delete_todo(todo_id: int) -> None:
    """Delete a todo by ID.

    Args:
        todo_id: Todo ID

    Raises:
        HTTPException: If todo not found (404)

    """
    success = await todo_service.delete(todo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Todo not found")

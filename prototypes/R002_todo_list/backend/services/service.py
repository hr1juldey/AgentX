# =============================================================================
# R002 Todo List - Service Layer
# =============================================================================
# Business logic for todo management with in-memory storage
# =============================================================================

from datetime import datetime, UTC

from models.schemas import Priority, Status, TodoCreate, TodoResponse, TodoUpdate


class TodoService:
    """Service for managing todos."""

    def __init__(self) -> None:
        """Initialize the service with empty todos storage."""
        self._todos: dict[int, TodoResponse] = {}
        self._next_id = 1

    async def create(self, todo: TodoCreate) -> TodoResponse:
        """Create a new todo.

        Args:
            todo: Todo creation data

        Returns:
            Created todo with ID and timestamps

        """
        now = datetime.now(UTC)
        todo_response = TodoResponse(
            id=self._next_id,
            title=todo.title,
            description=todo.description,
            due_date=todo.due_date,
            priority=todo.priority,
            status=todo.status,
            created_at=now,
            updated_at=now,
        )
        self._todos[self._next_id] = todo_response
        self._next_id += 1
        return todo_response

    async def get(self, todo_id: int) -> TodoResponse | None:
        """Get a todo by ID.

        Args:
            todo_id: Todo ID

        Returns:
            Todo if found, None otherwise

        """
        return self._todos.get(todo_id)

    async def list_all(
        self, status: Status | None = None, priority: Priority | None = None
    ) -> list[TodoResponse]:
        """List all todos with optional filtering.

        Args:
            status: Filter by status (optional)
            priority: Filter by priority (optional)

        Returns:
            List of todos matching filters, sorted by creation date (newest first)

        """
        todos = list(self._todos.values())

        # Apply filters
        if status is not None:
            todos = [t for t in todos if t.status == status]
        if priority is not None:
            todos = [t for t in todos if t.priority == priority]

        # Sort by creation date (newest first)
        return sorted(todos, key=lambda t: t.created_at, reverse=True)

    async def update(self, todo_id: int, todo_update: TodoUpdate) -> TodoResponse | None:
        """Update an existing todo.

        Args:
            todo_id: Todo ID
            todo_update: Todo update data

        Returns:
            Updated todo if found, None otherwise

        """
        existing = self._todos.get(todo_id)
        if existing is None:
            return None

        # Update fields if provided
        updated_todo = TodoResponse(
            id=existing.id,
            title=todo_update.title if todo_update.title is not None else existing.title,
            description=(
                todo_update.description
                if todo_update.description is not None
                else existing.description
            ),
            due_date=(
                todo_update.due_date
                if todo_update.due_date is not None
                else existing.due_date
            ),
            priority=(
                todo_update.priority if todo_update.priority is not None else existing.priority
            ),
            status=todo_update.status if todo_update.status is not None else existing.status,
            created_at=existing.created_at,
            updated_at=datetime.now(UTC),
        )
        self._todos[todo_id] = updated_todo
        return updated_todo

    async def delete(self, todo_id: int) -> bool:
        """Delete a todo by ID.

        Args:
            todo_id: Todo ID

        Returns:
            True if deleted, False if not found

        """
        if todo_id in self._todos:
            del self._todos[todo_id]
            return True
        return False


# Singleton instance
_todo_service: TodoService | None = None


def get_todo_service() -> TodoService:
    """Get the singleton todo service instance."""
    global _todo_service
    if _todo_service is None:
        _todo_service = TodoService()
    return _todo_service

# =============================================================================
# R003 Pomodoro Timer - Service Layer
# =============================================================================
# Business logic for Pomodoro timer management with in-memory storage
# =============================================================================

import asyncio
from datetime import UTC, datetime

from models.schemas import (
    SessionCreate,
    SessionResponse,
    SessionStatus,
    SessionUpdate,
)


class PomodoroService:
    """Service for managing Pomodoro timer sessions."""

    def __init__(self) -> None:
        """Initialize the service with empty sessions storage."""
        self._sessions: dict[int, SessionResponse] = {}
        self._next_id = 1
        self._timer_tasks: dict[int, asyncio.Task[None]] = {}
        self._websocket_connections: dict[int, set[asyncio.Queue]] = {}

    async def create(self, session: SessionCreate) -> SessionResponse:
        """Create a new Pomodoro session.

        Args:
            session: Session creation data

        Returns:
            Created session with ID and timestamps

        """
        now = datetime.now(UTC)

        # Handle legacy duration_minutes parameter
        work_duration = session.work_duration
        if session.duration_minutes is not None:
            work_duration = session.duration_minutes

        # Convert minutes to seconds
        total_seconds = work_duration * 60

        session_response = SessionResponse(
            id=self._next_id,
            title=session.title,
            status=SessionStatus.RUNNING,
            remaining_seconds=total_seconds,
            total_seconds=total_seconds,
            work_duration=session.work_duration,
            break_duration=session.break_duration,
            created_at=now,
            updated_at=now,
        )
        self._sessions[self._next_id] = session_response
        self._websocket_connections[self._next_id] = set()

        # Start the countdown timer
        self._timer_tasks[self._next_id] = asyncio.create_task(
            self._countdown(self._next_id)
        )

        self._next_id += 1
        return session_response

    async def get(self, session_id: int) -> SessionResponse | None:
        """Get a session by ID.

        Args:
            session_id: Session ID

        Returns:
            Session if found, None otherwise

        """
        return self._sessions.get(session_id)

    async def list_all(
        self, status: SessionStatus | None = None
    ) -> list[SessionResponse]:
        """List all sessions with optional filtering.

        Args:
            status: Filter by status (optional)

        Returns:
            List of sessions matching filters, sorted by creation date (newest first)

        """
        sessions = list(self._sessions.values())

        # Apply filters
        if status is not None:
            sessions = [s for s in sessions if s.status == status]

        # Sort by creation date (newest first)
        return sorted(sessions, key=lambda s: s.created_at, reverse=True)

    async def update(
        self, session_id: int, session_update: SessionUpdate
    ) -> SessionResponse | None:
        """Update an existing session.

        Args:
            session_id: Session ID
            session_update: Session update data

        Returns:
            Updated session if found, None otherwise

        """
        existing = self._sessions.get(session_id)
        if existing is None:
            return None

        # Handle status transitions
        new_status = (
            session_update.status
            if session_update.status is not None
            else existing.status
        )

        # If pausing, cancel the countdown task
        if (
            new_status == SessionStatus.PAUSED
            and existing.status == SessionStatus.RUNNING
        ):
            if session_id in self._timer_tasks:
                self._timer_tasks[session_id].cancel()
                del self._timer_tasks[session_id]

        # If resuming, restart the countdown
        if (
            new_status == SessionStatus.RUNNING
            and existing.status == SessionStatus.PAUSED
        ):
            self._timer_tasks[session_id] = asyncio.create_task(
                self._countdown(session_id)
            )

        # If cancelling, cancel the countdown and mark as cancelled
        if new_status == SessionStatus.CANCELLED:
            if session_id in self._timer_tasks:
                self._timer_tasks[session_id].cancel()
                del self._timer_tasks[session_id]

        # Update fields
        updated_session = SessionResponse(
            id=existing.id,
            title=existing.title,
            status=new_status,
            remaining_seconds=(
                session_update.remaining_seconds
                if session_update.remaining_seconds is not None
                else existing.remaining_seconds
            ),
            total_seconds=existing.total_seconds,
            work_duration=existing.work_duration,
            break_duration=existing.break_duration,
            created_at=existing.created_at,
            updated_at=datetime.now(UTC),
        )
        self._sessions[session_id] = updated_session

        # Broadcast update to WebSocket clients
        await self._broadcast_update(session_id, updated_session)

        return updated_session

    async def delete(self, session_id: int) -> bool:
        """Delete a session by ID.

        Args:
            session_id: Session ID

        Returns:
            True if deleted, False if not found

        """
        if session_id not in self._sessions:
            return False

        # Cancel timer if running
        if session_id in self._timer_tasks:
            self._timer_tasks[session_id].cancel()
            del self._timer_tasks[session_id]

        # Close WebSocket connections
        if session_id in self._websocket_connections:
            for queue in self._websocket_connections[session_id]:
                await queue.put(None)  # Signal connection close
            del self._websocket_connections[session_id]

        del self._sessions[session_id]
        return True

    async def register_websocket(self, session_id: int) -> asyncio.Queue | None:
        """Register a WebSocket connection for a session.

        Args:
            session_id: Session ID

        Returns:
            Queue for receiving updates, or None if session not found

        """
        if session_id not in self._sessions:
            return None

        queue: asyncio.Queue[SessionResponse | None] = asyncio.Queue()
        self._websocket_connections[session_id].add(queue)
        return queue

    async def unregister_websocket(self, session_id: int, queue: asyncio.Queue) -> None:
        """Unregister a WebSocket connection.

        Args:
            session_id: Session ID
            queue: The queue to remove

        """
        if session_id in self._websocket_connections:
            self._websocket_connections[session_id].discard(queue)

    async def _countdown(self, session_id: int) -> None:
        """Run the countdown timer for a session.

        Args:
            session_id: Session ID

        """
        try:
            while True:
                await asyncio.sleep(1)

                session = self._sessions.get(session_id)
                if session is None or session.status != SessionStatus.RUNNING:
                    break

                # Decrement remaining time
                new_remaining = session.remaining_seconds - 1

                if new_remaining <= 0:
                    # Timer completed
                    completed_session = SessionResponse(
                        id=session.id,
                        title=session.title,
                        status=SessionStatus.COMPLETED,
                        remaining_seconds=0,
                        total_seconds=session.total_seconds,
                        work_duration=session.work_duration,
                        break_duration=session.break_duration,
                        created_at=session.created_at,
                        updated_at=datetime.now(UTC),
                    )
                    self._sessions[session_id] = completed_session

                    # Broadcast completion
                    await self._broadcast_update(session_id, completed_session)
                    break
                else:
                    # Update remaining time
                    updated_session = SessionResponse(
                        id=session.id,
                        title=session.title,
                        status=session.status,
                        remaining_seconds=new_remaining,
                        total_seconds=session.total_seconds,
                        work_duration=session.work_duration,
                        break_duration=session.break_duration,
                        created_at=session.created_at,
                        updated_at=datetime.now(UTC),
                    )
                    self._sessions[session_id] = updated_session

                    # Broadcast update
                    await self._broadcast_update(session_id, updated_session)

        except asyncio.CancelledError:
            # Timer was cancelled (pause or cancel operation)
            pass

    async def _broadcast_update(
        self, session_id: int, session: SessionResponse
    ) -> None:
        """Broadcast session update to all WebSocket clients.

        Args:
            session_id: Session ID
            session: Updated session data

        """
        if session_id in self._websocket_connections:
            for queue in list(self._websocket_connections[session_id]):
                try:
                    await queue.put(session)
                except Exception:
                    # Remove failed queues
                    self._websocket_connections[session_id].discard(queue)


# Singleton instance
_pomodoro_service: PomodoroService | None = None


def get_pomodoro_service() -> PomodoroService:
    """Get the singleton Pomodoro service instance."""
    global _pomodoro_service
    if _pomodoro_service is None:
        _pomodoro_service = PomodoroService()
    return _pomodoro_service

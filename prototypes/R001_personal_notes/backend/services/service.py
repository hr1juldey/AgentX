# =============================================================================
# R001 Personal Notes - Service Layer
# =============================================================================
# Business logic for note management with in-memory storage
# =============================================================================

from datetime import UTC, datetime

from models.schemas import NoteCreate, NoteResponse, NoteUpdate


class NoteService:
    """Service for managing notes."""

    def __init__(self) -> None:
        """Initialize the service with empty notes storage."""
        self._notes: dict[int, NoteResponse] = {}
        self._next_id = 1

    async def create(self, note: NoteCreate) -> NoteResponse:
        """Create a new note.

        Args:
            note: Note creation data

        Returns:
            Created note with ID and timestamps

        """
        now = datetime.now(UTC)
        note_response = NoteResponse(
            id=self._next_id,
            title=note.title,
            content=note.content,
            created_at=now,
            updated_at=now,
        )
        self._notes[self._next_id] = note_response
        self._next_id += 1
        return note_response

    async def get(self, note_id: int) -> NoteResponse | None:
        """Get a note by ID.

        Args:
            note_id: Note ID

        Returns:
            Note if found, None otherwise

        """
        return self._notes.get(note_id)

    async def list_all(self) -> list[NoteResponse]:
        """List all notes sorted by creation date (newest first).

        Returns:
            List of all notes

        """
        return sorted(self._notes.values(), key=lambda n: n.created_at, reverse=True)

    async def update(self, note_id: int, note_update: NoteUpdate) -> NoteResponse | None:
        """Update an existing note.

        Args:
            note_id: Note ID
            note_update: Note update data

        Returns:
            Updated note if found, None otherwise

        """
        existing = self._notes.get(note_id)
        if existing is None:
            return None

        # Update fields if provided
        updated_note = NoteResponse(
            id=existing.id,
            title=note_update.title if note_update.title is not None else existing.title,
            content=note_update.content if note_update.content is not None else existing.content,
            created_at=existing.created_at,
            updated_at=datetime.now(UTC),
        )
        self._notes[note_id] = updated_note
        return updated_note

    async def delete(self, note_id: int) -> bool:
        """Delete a note by ID.

        Args:
            note_id: Note ID

        Returns:
            True if deleted, False if not found

        """
        if note_id in self._notes:
            del self._notes[note_id]
            return True
        return False


# Singleton instance
_note_service: NoteService | None = None


def get_note_service() -> NoteService:
    """Get the singleton note service instance."""
    global _note_service
    if _note_service is None:
        _note_service = NoteService()
    return _note_service

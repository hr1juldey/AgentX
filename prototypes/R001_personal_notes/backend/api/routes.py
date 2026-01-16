# =============================================================================
# R001 Personal Notes - API Routes
# =============================================================================
# FastAPI routes for note CRUD operations
# =============================================================================

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from models.schemas import NoteCreate, NoteResponse, NoteUpdate
from services.service import get_note_service

router = APIRouter(prefix="/notes", tags=["notes"])

# Service instance
note_service = get_note_service()


# -----------------------------------------------------------------------------
# Note Endpoints
# -----------------------------------------------------------------------------
@router.post("", response_model=NoteResponse, status_code=201)
async def create_note(note: NoteCreate) -> NoteResponse:
    """Create a new note.

    Args:
        note: Note creation data with title and content

    Returns:
        Created note with ID and timestamps

    """
    return await note_service.create(note)


@router.get("", response_model=dict)
async def list_notes(
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> dict[str, object]:
    """List all notes.

    Args:
        limit: Maximum number of notes to return (default: 50)

    Returns:
        Dictionary with notes list and total count

    """
    notes = await note_service.list_all()
    return {
        "notes": notes[:limit],
        "total": len(notes),
    }


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id: int) -> NoteResponse:
    """Get a note by ID.

    Args:
        note_id: Note ID

    Returns:
        Note data

    Raises:
        HTTPException: If note not found (404)

    """
    result = await note_service.get(note_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return result


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(note_id: int, note_update: NoteUpdate) -> NoteResponse:
    """Update an existing note.

    Args:
        note_id: Note ID
        note_update: Note update data (title and/or content)

    Returns:
        Updated note

    Raises:
        HTTPException: If note not found (404)

    """
    result = await note_service.update(note_id, note_update)
    if result is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return result


@router.delete("/{note_id}", status_code=204)
async def delete_note(note_id: int) -> None:
    """Delete a note by ID.

    Args:
        note_id: Note ID

    Raises:
        HTTPException: If note not found (404)

    """
    success = await note_service.delete(note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")

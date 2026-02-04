"""Memory-related API endpoints."""

from fastapi import APIRouter

from agentx.presentation.models.requests import MemoryRequest
from agentx.presentation.models.responses import MemoryResponse

router = APIRouter(prefix="/memory", tags=["memory"])


@router.post("/search", response_model=MemoryResponse)
async def search_memory(request: MemoryRequest) -> MemoryResponse:
    """Search memories for relevant context.

    Args:
        request: Memory search request

    Returns:
        Retrieved memories

    Raises:
        NotImplementedError: If not yet implemented
    """
    raise NotImplementedError("POST /memory/search not yet implemented")


@router.post("/add", response_model=MemoryResponse)
async def add_memory(request: MemoryRequest) -> MemoryResponse:
    """Add interaction to memory.

    Args:
        request: Memory addition request

    Returns:
        Storage result

    Raises:
        NotImplementedError: If not yet implemented
    """
    raise NotImplementedError("POST /memory/add not yet implemented")

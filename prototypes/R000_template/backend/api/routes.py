# =============================================================================
# AGENTX Prototype - API Routes
# =============================================================================
# FastAPI route definitions for the prototype
# =============================================================================

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from models.schemas import ItemCreate, ItemResponse
from services.service import get_item_service

router = APIRouter()

# Service instance
item_service = get_item_service()


# -----------------------------------------------------------------------------
# Health Check
# -----------------------------------------------------------------------------
@router.get("/health", response_model=dict)
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


# -----------------------------------------------------------------------------
# Item Endpoints (Example CRUD)
# -----------------------------------------------------------------------------
@router.post("/items", response_model=ItemResponse, status_code=201)
async def create_item(item: ItemCreate) -> ItemResponse:
    """Create a new item.

    Args:
        item: Item creation data

    Returns:
        Created item with assigned ID

    """
    return await item_service.create(item)


@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int) -> ItemResponse:
    """Get an item by ID.

    Args:
        item_id: Item ID

    Returns:
        Item data

    Raises:
        HTTPException: If item not found

    """
    result = await item_service.get(item_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return result


@router.get("/items", response_model=list[ItemResponse])
async def list_items(
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[ItemResponse]:
    """List all items.

    Args:
        limit: Maximum number of items to return

    Returns:
        List of items

    """
    items = await item_service.list_all()
    return items[:limit]


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int) -> None:
    """Delete an item by ID.

    Args:
        item_id: Item ID

    Raises:
        HTTPException: If item not found

    """
    success = await item_service.delete(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")

# =============================================================================
# AGENTX Prototype - Service Layer
# =============================================================================
# Business logic layer for data processing
# =============================================================================


from models.schemas import ItemCreate, ItemResponse


class ItemService:
    """Example service for item management."""

    def __init__(self) -> None:
        """Initialize the service."""
        self._items: dict[int, ItemResponse] = {}
        self._next_id = 1

    async def create(self, item: ItemCreate) -> ItemResponse:
        """Create a new item.

        Args:
            item: Item creation data

        Returns:
            Created item with ID

        """
        from datetime import datetime

        item_response = ItemResponse(
            id=self._next_id,
            name=item.name,
            description=item.description,
            created_at=datetime.utcnow().isoformat(),
        )
        self._items[self._next_id] = item_response
        self._next_id += 1
        return item_response

    async def get(self, item_id: int) -> ItemResponse | None:
        """Get an item by ID.

        Args:
            item_id: Item ID

        Returns:
            Item if found, None otherwise

        """
        return self._items.get(item_id)

    async def list_all(self) -> list[ItemResponse]:
        """List all items.

        Returns:
            List of all items

        """
        return list(self._items.values())

    async def delete(self, item_id: int) -> bool:
        """Delete an item by ID.

        Args:
            item_id: Item ID

        Returns:
            True if deleted, False if not found

        """
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False


# Singleton instance
_item_service: ItemService | None = None


def get_item_service() -> ItemService:
    """Get the singleton item service instance."""
    global _item_service
    if _item_service is None:
        _item_service = ItemService()
    return _item_service

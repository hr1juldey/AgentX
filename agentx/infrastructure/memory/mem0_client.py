"""Mem0AI client wrapper for AGENTX."""


class Mem0Client:
    """Wrapper for Mem0AI memory client."""

    def __init__(self) -> None:
        """Initialize the Mem0AI client.

        Raises:
            NotImplementedError: If not yet implemented
        """
        raise NotImplementedError("Mem0Client not yet implemented")

    async def search(self, query: str, user_id: str, limit: int = 5) -> list[dict]:
        """Search memories for relevant context.

        Args:
            query: Search query
            user_id: User identifier
            limit: Maximum results

        Returns:
            List of memory results

        Raises:
            NotImplementedError: If not yet implemented
        """
        raise NotImplementedError("Mem0Client.search() not yet implemented")

    async def add(self, messages: list[dict], user_id: str) -> dict:
        """Store interaction in memory.

        Args:
            messages: List of message dicts with role and content
            user_id: User identifier

        Returns:
            Storage result

        Raises:
            NotImplementedError: If not yet implemented
        """
        raise NotImplementedError("Mem0Client.add() not yet implemented")

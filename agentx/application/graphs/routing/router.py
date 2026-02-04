"""Router - Dynamic routing between graphs based on context."""

from agentx.domain.entities.graph import Graph


class Router:
    """Route between graphs based on execution context."""

    def __init__(self) -> None:
        """Initialize the router."""
        pass

    def select_graph(self, query: str, context: dict) -> Graph:
        """Select best graph for this query.

        Args:
            query: User query
            context: Additional context

        Returns:
            Selected Graph

        Raises:
            NotImplementedError: If not yet implemented
        """
        raise NotImplementedError("Router.select_graph() not yet implemented")

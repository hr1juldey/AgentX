"""Evaluator - Compare graph variations."""

from agentx.domain.entities.graph import Graph


class Evaluator:
    """Compare graph variations to select the best."""

    def __init__(self) -> None:
        """Initialize the evaluator."""
        pass

    def compare_variations(self, variations: list[Graph]) -> Graph:
        """Compare graph variations and return the best.

        Args:
            variations: List of graph variations

        Returns:
            Best Graph

        Raises:
            NotImplementedError: If not yet implemented
        """
        raise NotImplementedError("Evaluator.compare_variations() not yet implemented")

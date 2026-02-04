"""Critic - Evaluate graph execution quality."""

from agentx.domain.entities.execution import Execution


class Critic:
    """Evaluate graph execution and produce quality score."""

    def __init__(self) -> None:
        """Initialize the critic."""
        pass

    def evaluate(self, execution: Execution) -> float:
        """Score execution quality (0.0 to 1.0).

        Args:
            execution: Execution to evaluate

        Returns:
            Quality score

        Raises:
            NotImplementedError: If not yet implemented
        """
        raise NotImplementedError("Critic.evaluate() not yet implemented")

"""Coordinator - Decide continue/replan/mutate based on critic score."""

from agentx.application.evaluation.critic import Critic
from agentx.domain.entities.execution import Execution


class Coordinator:
    """Decide next action based on critic evaluation."""

    def __init__(self) -> None:
        """Initialize the coordinator."""
        pass

    def decide(self, execution: Execution, critic: Critic) -> str:
        """Return: 'continue', 'replan', or 'mutate'.

        Args:
            execution: Execution to evaluate
            critic: Critic to score execution

        Returns:
            Decision string

        Raises:
            NotImplementedError: If not yet implemented
        """
        raise NotImplementedError("Coordinator.decide() not yet implemented")

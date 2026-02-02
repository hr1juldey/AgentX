"""Base ReAct agent with tool limit enforcement.

This module provides the base class for all ReAct agents with
enforced tool limits to prevent hallucination.
"""

import dspy

from agentx.agent.dspy_signatures.main_signatures import BaseReActSignature

# Hard limit to prevent hallucination
MAX_TOOLS_PER_AGENT = 5


class BaseReActAgent(dspy.Module):
    """Base class with tool limit enforcement.

    Enforces MAX_TOOLS_PER_AGENT to prevent tool confusion and hallucination.
    Each sub-agent should have 3-5 tools maximum.
    """

    def __init__(self, tools: list[dspy.Tool], max_tools: int = MAX_TOOLS_PER_AGENT):
        """Initialize base ReAct agent.

        Args:
            tools: List of DSPy tools
            max_tools: Maximum tools allowed (default: MAX_TOOLS_PER_AGENT)

        Raises:
            ValueError: If too many tools provided
        """
        if len(tools) > max_tools:
            raise ValueError(
                f"Too many tools: {len(tools)} > {max_tools}. "
                f"Split into multiple sub-agents to prevent hallucination."
            )

        super().__init__()

        # Create ReAct with limited toolset
        self.react = dspy.ReAct(
            BaseReActSignature,  # type: ignore[arg-type]
            tools=tools,  # type: ignore[arg-type]
            max_iters=3,  # Limited iterations
        )

    def forward(self, query: str, **kwargs) -> dspy.Prediction:
        """Execute ReAct reasoning.

        Args:
            query: User query
            **kwargs: Additional context

        Returns:
            dspy.Prediction: ReAct result
        """
        result = self.react(query=query, **kwargs)
        return result  # type: ignore[bad-return]

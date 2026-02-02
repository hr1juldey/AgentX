"""Main DSPy ReAct agent.

Implements the primary agent using DSPy ReAct pattern.
"""

import dspy

from agentx.agent.dspy_signatures.main_signatures import MainAgentSignature
from agentx.agent.tools.main_tools import AVAILABLE_TOOLS


class MainDSPyReActAgent(dspy.Module):
    """Main ReAct agent for query processing.

    Uses DSPy ReAct pattern for multi-step reasoning with tools.
    """

    def __init__(self) -> None:
        """Initialize the main ReAct agent with tools."""
        super().__init__()
        self.react = dspy.ReAct(
            signature=MainAgentSignature,
            tools=AVAILABLE_TOOLS,  # type: ignore[arg-type]
            max_iters=5,
        )

    def forward(self, **kwargs) -> dspy.Prediction:
        """Process a user query.

        Args:
            **kwargs: Keyword arguments (query: str, context: str = "")

        Returns:
            dspy.Prediction: Agent response with reasoning.
        """
        return self.react(**kwargs)  # type: ignore[bad-return]

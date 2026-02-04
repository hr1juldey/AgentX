"""Researcher Agent - differentiated stem cell for research tasks."""

import dspy

from agentx.application.agents.stem_cell import StemCellAgent


class ResearcherAgent(StemCellAgent):
    """Researcher agent for search and research tasks.

    Differentiated via specialized signature:
    "query, context -> answer, reasoning, citations"
    """

    def __init__(self, user_id: str) -> None:
        """Initialize the researcher agent.

        Args:
            user_id: User identifier for memory isolation
        """
        # Create research-specific signature using standard DSPy pattern
        research_signature = dspy.Signature(  # type: ignore[call-arg]
            "query, context -> answer, reasoning, citations"
        )

        super().__init__(
            user_id=user_id, signature=research_signature, enable_tools=True
        )

        # Tools will be mounted during initialization
        # TODO: Add SearXNG search tool, web scraping tool, etc.

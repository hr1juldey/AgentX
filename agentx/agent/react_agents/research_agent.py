"""Research sub-agent with 3 tools.

This agent handles research operations with a focused toolset
to prevent hallucination.
"""

import dspy

from agentx.agent.react_agents.base_agent import BaseReActAgent


class ResearchAgent(BaseReActAgent):
    """Research specialist with ONLY 3 tools (prevents hallucination).

    Tools:
    1. search_web - Search the web for information
    2. scrape_page - Scrape content from a URL
    3. build_citation - Build citation from source

    Limited to 3 tools to prevent tool confusion.
    """

    def __init__(self, search_web, scrape_page, build_citation):
        """Initialize research agent with 3 tools.

        Args:
            search_web: Web search function
            scrape_page: Web scraper function
            build_citation: Citation builder function
        """
        tools = [
            dspy.Tool(search_web, name="search_web"),
            dspy.Tool(scrape_page, name="scrape_page"),
            dspy.Tool(build_citation, name="build_citation"),
        ]

        super().__init__(tools=tools, max_tools=3)

    def forward(self, query: str, **kwargs) -> dspy.Prediction:
        """Execute research with limited tools.

        Args:
            query: Research query
            **kwargs: Additional context (ignored)

        Returns:
            dspy.Prediction: Research findings with sources
        """
        result = self.react(query=query)

        # Extract research findings
        findings = result.result if hasattr(result, "result") else str(result)

        return dspy.Prediction(
            research_findings=findings,
            sources=getattr(result, "sources", []),
        )

"""Context Injector Module for Contextualizer agent.

Ported from R014: services/tools/contextualizer/contextualizer.py

Injects relevant context into research findings.
Enriches findings with additional context from various sources.
"""

import dspy

from agentx.agent.dspy_signatures.contextualizer.reranking import InjectContext
from agentx.agent.tools.common.dspy_helpers import safe_extract


class ContextInjectorModule(dspy.Module):
    """Injects relevant context into research findings.

    Enriches findings by:
    - Weaving in relevant context naturally
    - Adding citations for all sources
    - Maintaining coherence and readability
    - Preserving original findings structure
    """

    def __init__(self) -> None:
        """Initialize the context injector."""
        super().__init__()
        self.injector = dspy.ChainOfThought(InjectContext)

    def forward(
        self,
        findings: str,
        context: list[dict],
        query: str,
    ) -> dict:
        """Inject context into research findings.

        Args:
            findings: Original research findings
            context: List of context dicts to inject
            query: Original user query

        Returns:
            dict with 'enriched_findings' (str) and 'injected_count' (int)
        """
        if not context:
            return {
                "enriched_findings": findings,
                "injected_count": 0,
            }

        # Build context string
        context_str = self._format_context(context)

        # Run injector
        result = self.injector(
            findings=findings,
            context=context_str,
            query=query,
        )

        # Extract enriched findings
        enriched_findings = safe_extract(result, "enriched_findings", findings)

        # Count how many context chunks were used
        injected_count = self._count_injected_context(enriched_findings, context)

        return {
            "enriched_findings": enriched_findings,
            "injected_count": injected_count,
        }

    def _format_context(self, context: list[dict]) -> str:
        """Format context list as string.

        Args:
            context: List of context dicts

        Returns:
            str: Formatted context string
        """
        lines: list[str] = []
        for i, chunk in enumerate(context, 1):
            text = chunk.get("text", "")
            source = chunk.get("source", "Unknown")
            lines.append(f"Context {i} (from {source}):")
            lines.append(f"  {text}")
            lines.append("")

        return "\n".join(lines)

    def _count_injected_context(
        self, enriched_findings: str, context: list[dict]
    ) -> int:
        """Count how many context chunks were injected.

        Args:
            enriched_findings: Enriched findings text
            context: Original context list

        Returns:
            int: Number of context chunks injected
        """
        count = 0
        for chunk in context:
            text = chunk.get("text", "")
            if text and text.lower() in enriched_findings.lower():
                count += 1

        return count

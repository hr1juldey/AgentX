# =============================================================================
# AGENTX Researcher - Report Generator Module
# =============================================================================
# DSPy module for generating micro reports from filtered content
# =============================================================================

import dspy
import re


class GenerateMicroReport(dspy.Signature):
    """Generate a 2-4 sentence micro report that addresses the research goal.

    Include specific facts with source attribution. Be concise and factual.
    Avoid fluff and redundancy.
    """

    research_goal: str = dspy.InputField(desc="Research question or goal")
    content: str = dspy.InputField(desc="Filtered relevant content (max 1000 chars)")
    source_url: str = dspy.InputField(desc="URL of the source page")

    micro_report: str = dspy.OutputField(
        desc="2-4 sentence report addressing the goal with specific facts and source attribution"
    )


class ReportGeneratorModule(dspy.Module):
    """Generates micro reports from filtered content.

    Uses the GenerateMicroReport signature to create concise,
    factual reports with source attribution.
    """

    def __init__(self):
        super().__init__()
        self.generate = dspy.Predict(GenerateMicroReport)

    def generate_report(self, content: str, goal: str, source_url: str) -> dict:
        """Generate a micro report from filtered content.

        Args:
            content: Filtered relevant content
            goal: Research goal
            source_url: Source URL for attribution

        Returns:
            Dict with report and word_count
        """
        result = self.generate(
            content=content, research_goal=goal, source_url=source_url
        )

        report = result.micro_report  # type: ignore[attr-defined]

        # Count words (simple split by whitespace)
        word_count = len(re.findall(r"\S+", report)) if report else 0

        return {"report": report, "word_count": word_count}

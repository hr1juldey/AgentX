# =============================================================================
# AGENTX Researcher - Report Generator Module
# =============================================================================
# DSPy module for generating micro reports from filtered content
# =============================================================================

import dspy


class GenerateMicroReport(dspy.Signature):
    """Generate a concise micro report from research content.

    Output should be:
    1. Concise (2-4 sentences)
    2. Focused on answering the research goal
    3. Include specific facts/data with sources
    4. Avoid fluff and redundancy

    Examples:
        Goal: "What is the economic impact of climate change?"
        Content: "Climate change could reduce global GDP by 23% by 2100
        according to Swiss Re Institute. The World Bank estimates that
        climate change could push 100 million people into poverty by 2030."
        Output: "Climate change could reduce global GDP by 23% by 2100
        (Swiss Re Institute). Additionally, the World Bank estimates
        climate change may push 100 million people into poverty by 2030."

        Goal: "How does async/await work in Python?"
        Content: "Async functions use coroutines that can suspend execution.
        The 'await' keyword yields control back to the event loop. When
        the awaited operation completes, execution resumes."
        Output: "Async functions use coroutines that can suspend execution.
        The 'await' keyword yields control to the event loop, allowing
        other tasks to run. Execution resumes when the awaited operation
        completes."
    """

    research_goal: str = dspy.InputField(
        desc="The research question or goal we're trying to address"
    )
    content: str = dspy.InputField(
        desc="Filtered relevant content from web pages (max 1000 chars)"
    )
    source_url: str = dspy.InputField(desc="URL of the source page")
    micro_report: str = dspy.OutputField(
        desc="2-4 sentence report that directly addresses the goal. "
        "Include specific facts with source attribution. "
        "Be concise and factual."
    )


class ReportGeneratorModule(dspy.Module):
    """Generates micro reports from research content.

    Each report:
    - Is 2-4 sentences
    - Directly addresses the research goal
    - Includes source attribution
    - Avoids fluff and redundancy
    """

    MAX_CONTENT_PER_REPORT = 1000

    def __init__(self):
        super().__init__()
        self.generator = dspy.Predict(GenerateMicroReport)

    def generate_report(
        self,
        content: str,
        goal: str,
        source_url: str,
    ) -> dict:
        """Generate a micro report from content.

        Args:
            content: Filtered relevant content
            goal: Research goal
            source_url: Source URL for citation

        Returns:
            Dict with report, source_url, and word_count
        """
        # Truncate content to avoid context rotting
        truncated = content[: self.MAX_CONTENT_PER_REPORT]

        result = self.generator(
            research_goal=goal,
            content=truncated,
            source_url=source_url,
        )

        report = getattr(result, "micro_report", "")

        return {
            "report": report.strip(),
            "source_url": source_url,
            "word_count": len(report.split()),
        }

    def generate_multiple_reports(
        self,
        contents: list[dict],
        goal: str,
    ) -> list[dict]:
        """Generate reports from multiple pages.

        Args:
            contents: List of dicts with 'content' and 'url' keys
            goal: Research goal

        Returns:
            List of report dicts
        """
        reports = []

        for item in contents:
            if not item.get("content"):
                continue

            report = self.generate_report(
                content=item["content"],
                goal=goal,
                source_url=item["url"],
            )

            if report["report"]:
                reports.append(report)

        return reports

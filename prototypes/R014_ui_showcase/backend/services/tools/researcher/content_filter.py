# =============================================================================
# AGENTX Researcher - Content Filter Module
# =============================================================================
# DSPy module for filtering relevant content from web pages
# =============================================================================

import dspy


class FilterRelevantContent(dspy.Signature):
    """Filter content to find only relevant parts for the research goal.

    Input: A chunk of web page content (max 2000 chars) + research goal
    Output: Only the relevant sentences/paragraphs that help answer the goal

    Examples:
        Input chunk: "The company was founded in 2010. We have a 30-day return
        policy. Click here for our privacy policy. Our AI product uses advanced
        machine learning for natural language processing."
        Goal: "What AI technology does this company use?"
        Output: "Our AI product uses advanced machine learning for natural
        language processing."

        Input chunk: "Contact us at sales@example.com. Terms of service apply.
        The solution costs $99/month. Our customer support is available 24/7."
        Goal: "What is the pricing?"
        Output: "The solution costs $99/month."
    """

    content_chunk: str = dspy.InputField(desc="Web page content (max 2000 chars)")
    goal: str = dspy.InputField(desc="Research goal or question we're trying to answer")
    relevant_content: str = dspy.OutputField(
        desc="Only the relevant sentences that directly address the goal. "
        "If nothing relevant, output 'NONE'. Keep original wording."
    )


class ExtractRelevantLinks(dspy.Signature):
    """Identify which links are worth following based on research goal.

    Input: List of link descriptions (URL + text) + research goal
    Output: URLs that are likely to contain relevant information

    Examples:
        Goal: "Learn about Python async programming"
        Links:
        - "https://example.com/privacy" - Privacy Policy
        - "https://docs.python.org/async" - Async Documentation
        - "https://shop.example.com" - Store
        Output: "https://docs.python.org/async" with explanation

        Goal: "Company financial information"
        Links:
        - "https://ir.company.com" - Investor Relations
        - "https://company.com/careers" - Jobs
        Output: "https://ir.company.com" with explanation
    """

    links_summary: str = dspy.InputField(
        desc="List of links in format: URL | Text (max 10 links)"
    )
    goal: str = dspy.InputField(desc="Research goal or question we're trying to answer")
    relevant_urls: str = dspy.OutputField(
        desc="URLs worth following, one per line with | and brief reason. "
        "Example: 'https://example.com/page | Has detailed guide on topic'. "
        "Max 3 URLs. If none relevant, output 'NONE'."
    )


class ContentFilterModule(dspy.Module):
    """Filters web content to find relevant parts for research goal.

    Uses two DSPy predictors:
    1. FilterRelevantContent: Extract relevant sentences from page content
    2. ExtractRelevantLinks: Identify which links to follow next
    """

    MAX_CONTENT_LENGTH = 2000

    def __init__(self):
        super().__init__()
        self.content_filter = dspy.Predict(FilterRelevantContent)
        self.link_extractor = dspy.Predict(ExtractRelevantLinks)

    def filter_content(self, page_content: str, goal: str) -> str:
        """Extract only relevant content from a page.

        Args:
            page_content: Full page markdown content
            goal: Research goal

        Returns:
            Relevant content only, or empty string if nothing relevant
        """
        # Truncate to avoid context rotting
        chunk = page_content[: self.MAX_CONTENT_LENGTH]

        result = self.content_filter(content_chunk=chunk, goal=goal)

        relevant = getattr(result, "relevant_content", "")

        # Check if LLM found nothing relevant
        if not relevant or relevant.strip().upper() == "NONE":
            return ""

        return relevant.strip()

    def extract_links(self, links: list[dict], goal: str) -> list[dict]:
        """Identify which links are worth following.

        Args:
            links: List of dicts with 'url' and 'text' keys
            goal: Research goal

        Returns:
            List of relevant link dicts with 'reason' field added
        """
        if not links:
            return []

        # Build links summary (limit to 10 to avoid bloat)
        links_summary = "\n".join(
            [f"{link['url']} | {link.get('text', '')[:80]}" for link in links[:10]]
        )

        result = self.link_extractor(links_summary=links_summary, goal=goal)

        relevant_urls = getattr(result, "relevant_urls", "")

        # Parse results
        relevant_links = []
        for line in relevant_urls.split("\n"):
            line = line.strip()
            if not line or line.upper() == "NONE":
                continue

            # Parse "URL | reason" format
            if "|" in line:
                url_part = line.split("|")[0].strip()
                reason = line.split("|", 1)[1].strip() if "|" in line else ""

                # Find matching link from original list
                for link in links:
                    if link["url"] == url_part:
                        relevant_links.append(
                            {
                                "url": link["url"],
                                "text": link.get("text", ""),
                                "reason": reason,
                            }
                        )
                        break

        return relevant_links[:3]  # Limit to 3 links per page

# =============================================================================
# AGENTX Researcher - Citation Builder Module
# =============================================================================
# Builds citations from search results using position prediction
# =============================================================================

import dspy
import re


class FindBestCitationSpot(dspy.Signature):
    """Find best sentence to place citation link."""

    sentence: str = dspy.InputField(desc="Sentence to evaluate")
    source_info: str = dspy.InputField(desc="Source: Title | URL")
    relevance_score: str = dspy.OutputField(
        desc="Relevance score 0.0 to 1.0 for how well this sentence matches the source. "
        "0.0 = no relation, 1.0 = directly uses facts from source."
    )
    rationale: str = dspy.OutputField(desc="Brief explanation of relevance")


class CitationBuilderModule(dspy.Module):
    """Builds citations by finding best insertion spots in writing."""

    RELEVANCE_THRESHOLD = 0.5

    def __init__(self):
        super().__init__()
        self.spot_finder = dspy.ChainOfThought(FindBestCitationSpot)

    def _parse_relevance_score(self, score_str: str) -> float:
        """Parse relevance score from LLM output with fallback."""
        if not score_str:
            return 0.0

        # Try to extract a number
        match = re.search(r"0?\.\d+|1\.0|0|1", score_str)
        if match:
            try:
                return float(match.group())
            except (ValueError, IndexError):
                pass

        # Fallback: check for positive keywords
        positive = ["high", "relevant", "direct", "strong", "yes"]
        if any(word in score_str.lower() for word in positive):
            return 0.7

        return 0.0

    def forward(self, raw_data: list, writing: str = "") -> list:
        """Build citations from raw search results.

        Args:
            raw_data: List of search results with title/url/snippet
            writing: Existing writing to place citations in

        Returns:
            List of citation dicts
        """
        citations = []

        # If no writing, return basic citations
        if not writing:
            for index, item in enumerate(raw_data[:5]):
                citations.append(
                    {
                        "cited_text": item.get("content", "")[:200],
                        "document_index": index,
                        "document_title": item.get("title", ""),
                        "url": item.get("url", ""),
                    }
                )
            return citations

        # Find best spots for each source
        sentences = writing.split(". ")

        for index, source in enumerate(raw_data[:5]):
            source_info = f"{source.get('title', '')} | {source.get('url', '')}"

            best_sentence = None
            best_score = 0.0

            # Check each sentence (limit to 10 for efficiency)
            for sentence in sentences[:10]:
                result = self.spot_finder(sentence=sentence, source_info=source_info)

                # Parse relevance score with proper fallback
                score = self._parse_relevance_score(result.relevance_score)

                if score > self.RELEVANCE_THRESHOLD and score > best_score:
                    best_score = score
                    best_sentence = sentence

            if best_sentence:
                citations.append(
                    {
                        "cited_text": best_sentence[:200],
                        "document_index": index,
                        "document_title": source.get("title", ""),
                        "url": source.get("url", ""),
                    }
                )

        return citations

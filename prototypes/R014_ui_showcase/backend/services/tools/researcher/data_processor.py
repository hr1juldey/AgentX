# =============================================================================
# AGENTX Researcher - Data Processor Modules
# =============================================================================
# Beautifies and structures data for presentation
# =============================================================================

import dspy


class BeautifierModule(dspy.Module):
    """Beautifies raw search data for presentation.

    Has 3 signatures:
    - ExtractKeyFacts: Extract key facts from results
    - IdentifyTrends: Identify trends in data
    - CreateComparisons: Create comparisons between entities
    """

    def __init__(self):
        super().__init__()
        self.extract_facts = dspy.Predict("raw_data -> key_facts")
        self.identify_trends = dspy.Predict("raw_data -> trends")
        self.create_comparisons = dspy.Predict("raw_data, query -> comparisons")

    def forward(self, raw_data: list, query: str) -> dict:
        """Beautify raw search data."""
        facts_result = self.extract_facts(raw_data=str(raw_data[:5]))
        trends_result = self.identify_trends(raw_data=str(raw_data[:5]))
        comparisons_result = self.create_comparisons(
            raw_data=str(raw_data[:5]), query=query
        )

        return {
            "key_facts": [facts_result.key_facts]
            if hasattr(facts_result, "key_facts")
            else [],
            "trends": [trends_result.trends]
            if hasattr(trends_result, "trends")
            else [],
            "comparisons": [comparisons_result.comparisons]
            if hasattr(comparisons_result, "comparisons")
            else [],
        }


class DataStructurerModule(dspy.Module):
    """Structures data for better organization.

    Has 2 signatures:
    - OrganizeByTopic: Organize results by topic
    - CreateHierarchy: Create hierarchical structure
    """

    def __init__(self):
        super().__init__()
        self.organize_topic = dspy.Predict("beautiful_data -> organized_data")
        self.create_hierarchy = dspy.Predict("organized_data -> hierarchy")

    def forward(self, beautiful_data: dict) -> dict:
        """Structure the beautiful data."""
        organized_result = self.organize_topic(beautiful_data=str(beautiful_data))
        hierarchy_result = self.create_hierarchy(organized_data=str(organized_result))

        return {
            "structured_data": organized_result.organized_data,  # type: ignore[attr-defined]
            "hierarchy": hierarchy_result.hierarchy,  # type: ignore[attr-defined]
        }

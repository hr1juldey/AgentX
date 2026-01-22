# =============================================================================
# AGENTX Analyst - Query Analyzer Modules
# =============================================================================
# Analyzes query context and extracts insights
# =============================================================================

import dspy


class ContextAnalyzerModule(dspy.Module):
    """Analyzes the context and domain of the user query.

    Has 3 signatures:
    - DetectType: Detect query type (factual, analytical, creative)
    - ExtractDomain: Extract domain (finance, tech, health, etc.)
    - IdentifyUrgency: Identify urgency level
    """

    def __init__(self):
        super().__init__()
        self.detect_type = dspy.Predict("query -> query_type")
        self.extract_domain = dspy.Predict("query -> domain")
        self.identify_urgency = dspy.Predict("query -> urgency")

    def forward(self, query: str) -> dict:
        """Analyze query context."""
        type_result = self.detect_type(query=query)
        domain_result = self.extract_domain(query=query)
        urgency_result = self.identify_urgency(query=query)

        return {
            "query_type": type_result.query_type,  # type: ignore[attr-defined]
            "domain": domain_result.domain,  # type: ignore[attr-defined]
            "urgency": urgency_result.urgency,  # type: ignore[attr-defined]
        }


class InsightExtractorModule(dspy.Module):
    """Extracts key insights from the user query.

    Has 2 signatures:
    - ExtractInsights: Extract what the user really wants
    - IdentifyKeyQuestions: Identify underlying questions
    """

    def __init__(self):
        super().__init__()
        self.extract_insights = dspy.Predict("query -> insights")
        self.identify_questions = dspy.Predict("query -> key_questions")

    def forward(self, query: str) -> dict:
        """Extract insights from query."""
        insights_result = self.extract_insights(query=query)
        questions_result = self.identify_questions(query=query)

        return {
            "insights": insights_result.insights,  # type: ignore[attr-defined]
            "key_questions": questions_result.key_questions,  # type: ignore[attr-defined]
        }

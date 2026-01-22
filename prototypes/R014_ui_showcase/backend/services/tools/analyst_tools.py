# =============================================================================
# AGENTX Analyst Tools
# =============================================================================
# DSPy modules for the ANALYST agent (Reasoning + Judgment)
# =============================================================================

import dspy


# =============================================================================
# DSPy Signatures with proper type annotations
# =============================================================================


class AssessCompletenessSignature(dspy.Signature):
    """Assess if data is complete for answering the query."""

    query: str = dspy.InputField(desc="User query to evaluate")
    data: str = dspy.InputField(desc="Research data to assess")
    completeness_score: float = dspy.OutputField(
        desc="Completeness score from 0.0 to 1.0"
    )
    missing_elements: str = dspy.OutputField(desc="Description of missing information")


class AssessRelevanceSignature(dspy.Signature):
    """Assess if data is relevant to the query."""

    query: str = dspy.InputField(desc="User query")
    data: str = dspy.InputField(desc="Research data to evaluate")
    relevance_score: float = dspy.OutputField(desc="Relevance score from 0.0 to 1.0")
    relevance_explanation: str = dspy.OutputField(
        desc="Explanation of relevance assessment"
    )


class DecideResearchSignature(dspy.Signature):
    """Decide if more research is needed."""

    completeness_score: float = dspy.InputField(desc="Current completeness score")
    relevance_score: float = dspy.InputField(desc="Current relevance score")
    needs_more_research: bool = dspy.OutputField(desc="Whether more research is needed")
    reason: str = dspy.OutputField(desc="Reason for the decision")


# =============================================================================
# DSPy Modules
# =============================================================================


def _to_float(value: str | float | bool | None, default: float = 0.5) -> float:
    """Convert LLM output to float with fallbacks.

    Handles:
    - Already-float values
    - String floats ("0.75")
    - Text scores ("High" -> 0.9, "Medium" -> 0.5, "Low" -> 0.2)
    - Booleans (True -> 1.0, False -> 0.0)
    - Percentages ("75%" -> 0.75)

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Float value
    """
    if value is None:
        return default
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return default

    value_clean = value.strip().lower()

    # Text-based scores
    text_map = {
        "very high": 0.95,
        "high": 0.85,
        "good": 0.75,
        "medium": 0.50,
        "moderate": 0.50,
        "low": 0.25,
        "very low": 0.15,
        "poor": 0.20,
    }
    if value_clean in text_map:
        return text_map[value_clean]

    # Percentage format
    if "%" in value_clean:
        try:
            return float(value_clean.replace("%", "")) / 100.0
        except ValueError:
            pass

    # Direct float conversion
    try:
        return float(value_clean)
    except ValueError:
        return default


def _to_bool(value: str | bool | None, default: bool = False) -> bool:
    """Convert LLM output to bool with fallbacks.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Boolean value
    """
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if not isinstance(value, str):
        return default

    value_clean = value.strip().lower()
    true_values = {"true", "yes", "1", "t", "y", "high", "good", "very high"}
    false_values = {"false", "no", "0", "f", "n", "low", "poor", "very low"}

    if value_clean in true_values:
        return True
    if value_clean in false_values:
        return False
    return default


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


class GoalDetectorModule(dspy.Module):
    """Detects the goal and scope of the query.

    Has 3 signatures:
    - DetectGoal: Detect primary goal
    - DetectScope: Detect scope (broad, specific, comparison)
    - DetectDepth: Detect required depth (shallow, deep, comprehensive)
    """

    def __init__(self):
        super().__init__()
        self.detect_goal = dspy.Predict("query, insights -> goal")
        self.detect_scope = dspy.Predict("query -> scope")
        self.detect_depth = dspy.Predict("query, goal -> depth")

    def forward(self, query: str, insights: list) -> dict:
        """Detect goal and scope."""
        goal_result = self.detect_goal(query=query, insights=str(insights))
        scope_result = self.detect_scope(query=query)
        depth_result = self.detect_depth(query=query, goal=goal_result.goal)  # type: ignore[attr-defined]

        return {
            "goal": goal_result.goal,  # type: ignore[attr-defined]
            "scope": scope_result.scope,  # type: ignore[attr-defined]
            "depth": depth_result.depth,  # type: ignore[attr-defined]
        }


class DataQualityCheckerModule(dspy.Module):
    """Assesses data quality and completeness (for ANALYST Pass 2).

    Has 3 signatures:
    - AssessCompleteness: Assess if data is complete (returns float)
    - AssessRelevance: Assess if data is relevant to query (returns float)
    - DecideResearch: Decide if more research is needed (uses float inputs)
    """

    def __init__(self):
        super().__init__()
        # Use class-based signatures with float type annotations
        self.assess_completeness = dspy.Predict(AssessCompletenessSignature)
        self.assess_relevance = dspy.Predict(AssessRelevanceSignature)
        self.decide_research = dspy.Predict(DecideResearchSignature)

    def forward(self, query: str, data: dict) -> dict:
        """Assess data quality."""
        completeness_result = self.assess_completeness(query=query, data=str(data))
        relevance_result = self.assess_relevance(query=query, data=str(data))

        # Safely convert scores to float (handles text values like "High")
        completeness_score = _to_float(
            completeness_result.completeness_score  # type: ignore[attr-defined]
        )
        relevance_score = _to_float(
            relevance_result.relevance_score  # type: ignore[attr-defined]
        )

        decision_result = self.decide_research(
            completeness_score=completeness_score,
            relevance_score=relevance_score,
        )

        # Safely convert bool
        needs_more_research = _to_bool(
            decision_result.needs_more_research,  # type: ignore[attr-defined]
            default=(completeness_score < 0.7),
        )

        return {
            "data_quality": "high" if completeness_score > 0.7 else "low",
            "data_completeness": completeness_score,
            "query_relevance": relevance_score,
            "needs_more_research": needs_more_research,
            "reason": decision_result.reason,  # type: ignore[attr-defined]
        }

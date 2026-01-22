# =============================================================================
# AGENTX Presenter Tools
# =============================================================================
# DSPy modules for the PRESENTER agent (Final Polish + QA)
# =============================================================================

import dspy


class FlowCheckerModule(dspy.Module):
    """Checks narrative flow and pacing.

    Has 2 signatures:
    - CheckNarrativeFlow: Check if widgets tell a coherent story
    - ValidatePacing: Check if pacing is appropriate
    """

    def __init__(self):
        super().__init__()
        self.check_flow = dspy.Predict("sequence, widgets -> flow_analysis, issues")
        self.validate_pacing = dspy.Predict("delays -> pacing_analysis, issues")

    def forward(self, sequence: list, widgets: list) -> dict:
        """Check narrative flow and pacing."""
        sequence_str = str(sequence)
        widgets_str = str(widgets)

        flow_result = self.check_flow(sequence=sequence_str, widgets=widgets_str)

        # Extract delays from sequence for pacing validation
        delays = [s.get("delay_sec", 0) for s in sequence]
        pacing_result = self.validate_pacing(delays=str(delays))

        return {
            "flow_analysis": flow_result.flow_analysis
            if hasattr(flow_result, "flow_analysis")
            else "Coherent flow",
            "flow_issues": flow_result.issues if hasattr(flow_result, "issues") else [],
            "pacing_analysis": pacing_result.pacing_analysis
            if hasattr(pacing_result, "pacing_analysis")
            else "Appropriate pacing",
            "pacing_issues": pacing_result.issues
            if hasattr(pacing_result, "issues")
            else [],
        }


class PolisherModule(dspy.Module):
    """Polishes widget content for clarity and impact.

    Has 3 signatures:
    - PolishContent: Polish content for clarity
    - EnhanceClarity: Enhance clarity of messaging
    - AddTransitions: Add smooth transitions between widgets
    """

    def __init__(self):
        super().__init__()
        self.polish_content = dspy.Predict("content -> polished_content")
        self.enhance_clarity = dspy.Predict("content -> enhanced_content")
        self.add_transitions = dspy.Predict(
            "widgets, sequence -> transition_suggestions"
        )

    def forward(self, widgets: list, sequence: list) -> dict:
        """Polish widget content."""
        widgets_str = str(widgets)
        sequence_str = str(sequence)

        polish_result = self.polish_content(content=widgets_str)
        clarity_result = self.enhance_clarity(content=widgets_str)
        transition_result = self.add_transitions(
            widgets=widgets_str, sequence=sequence_str
        )

        return {
            "polished_content": polish_result.polished_content
            if hasattr(polish_result, "polished_content")
            else widgets_str,
            "enhanced_content": clarity_result.enhanced_content
            if hasattr(clarity_result, "enhanced_content")
            else widgets_str,
            "transition_suggestions": transition_result.transition_suggestions
            if hasattr(transition_result, "transition_suggestions")
            else [],
        }


class QAFinalizerModule(dspy.Module):
    """Performs final QA checks before sending to frontend.

    Has 4 signatures:
    - FinalQualityCheck: Overall quality check
    - FinalAccessibilityCheck: Accessibility compliance check
    - FinalFormatCheck: Format consistency check
    - ValidateSequence: Validate final sequence
    """

    def __init__(self):
        super().__init__()
        self.quality_check = dspy.Predict("widgets -> quality_score, issues")
        self.accessibility_check = dspy.Predict(
            "widgets -> accessibility_score, issues"
        )
        self.format_check = dspy.Predict("widgets -> format_score, issues")
        self.validate_sequence = dspy.Predict("widgets, sequence -> is_valid, issues")

    def forward(self, widgets: list, sequence: list) -> dict:
        """Perform final QA checks."""
        widgets_str = str(widgets)
        sequence_str = str(sequence)

        quality_result = self.quality_check(widgets=widgets_str)
        accessibility_result = self.accessibility_check(widgets=widgets_str)
        format_result = self.format_check(widgets=widgets_str)
        valid_result = self.validate_sequence(
            widgets=widgets_str, sequence=sequence_str
        )

        all_passed = all(
            [
                self._is_passed(quality_result),
                self._is_passed(accessibility_result),
                self._is_passed(format_result),
                self._is_passed(valid_result),
            ]
        )

        issues = []
        issues.extend(self._extract_issues(quality_result))
        issues.extend(self._extract_issues(accessibility_result))
        issues.extend(self._extract_issues(format_result))
        issues.extend(self._extract_issues(valid_result))

        return {
            "quality_check": "passed" if self._is_passed(quality_result) else "failed",
            "accessibility_check": "passed"
            if self._is_passed(accessibility_result)
            else "failed",
            "format_check": "passed" if self._is_passed(format_result) else "failed",
            "sequence_check": "passed" if self._is_passed(valid_result) else "failed",
            "all_passed": all_passed,
            "issues": issues,
            "ready_to_send": all_passed,
        }

    def _is_passed(self, result) -> bool:
        """Check if a result passed."""
        score_attr = (
            getattr(result, "quality_score", None)
            or getattr(result, "accessibility_score", None)
            or getattr(result, "format_score", None)
        )
        if score_attr:
            try:
                return float(score_attr) >= 0.7
            except (ValueError, TypeError):
                pass
        return getattr(result, "is_valid", "true") == "true"

    def _extract_issues(self, result) -> list:
        """Extract issues from a result."""
        if hasattr(result, "issues"):
            issues_str = str(result.issues)
            return [issue.strip() for issue in issues_str.split(",") if issue.strip()]
        return []

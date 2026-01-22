# =============================================================================
# AGENTX Presenter - QA Finalizer Module
# =============================================================================
# Performs final QA checks before sending to frontend
# =============================================================================

import dspy


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

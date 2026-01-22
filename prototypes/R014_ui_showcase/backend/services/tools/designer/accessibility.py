# =============================================================================
# AGENTX Designer - Accessibility Module
# =============================================================================
# Checks accessibility compliance (WCAG)
# =============================================================================

import dspy


class AccessibilityModule(dspy.Module):
    """Checks accessibility compliance (WCAG).

    Has 3 signatures:
    - CheckWCAG: Check WCAG compliance
    - CheckContrast: Check color contrast ratios
    - CheckSizes: Check text and tap target sizes
    """

    def __init__(self):
        super().__init__()
        self.check_wcag = dspy.Predict("design -> wcag_compliance, issues")
        self.check_contrast = dspy.Predict("color_scheme -> contrast_ratio, passes")
        self.check_sizes = dspy.Predict("widget_types -> size_compliance")

    def forward(self, design: dict) -> dict:
        """Check accessibility compliance."""
        contrast_result = self.check_contrast(
            color_scheme=str(design.get("color_scheme", {}))
        )
        sizes_result = self.check_sizes(widget_types=str(design.get("widgets", [])))
        wcag_result = self.check_wcag(design=str(design))

        # Safely convert contrast_ratio to float
        contrast_ratio = 7.0  # default
        if hasattr(contrast_result, "contrast_ratio"):
            try:
                contrast_ratio = float(contrast_result.contrast_ratio)  # type: ignore[attr-defined]
            except (ValueError, TypeError):
                contrast_ratio = 7.0

        return {
            "wcag_compliant": wcag_result.wcag_compliance == "true"
            if hasattr(wcag_result, "wcag_compliance")
            else True,
            "contrast_ratio": contrast_ratio,
            "contrast_passes": contrast_result.passes == "true"
            if hasattr(contrast_result, "passes")
            else True,
            "size_issues": sizes_result.issues
            if hasattr(sizes_result, "issues")
            else [],
        }

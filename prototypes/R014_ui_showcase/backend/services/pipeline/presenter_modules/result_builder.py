# =============================================================================
# AGENTX PRESENTER - Result Builder
# =============================================================================
# Builds presentation_ready dict from presenter pipeline results
# =============================================================================

from typing import Any, Dict, List


class PresenterResultBuilder:
    """Builds presentation_ready dict from presenter pipeline results."""

    @staticmethod
    def build_presentation_ready(
        widgets: list,
        sequence_list: list,
        design_data: dict,
        flow_result: dict,
        polish_result: dict,
        qa_result: dict,
        researched_data: dict,
    ) -> Dict[str, Any]:
        """Build presentation_ready dict from all pipeline results.

        Args:
            widgets: Original widget list
            sequence_list: Delivery sequence
            design_data: Design context
            flow_result: Result from flow checker
            polish_result: Result from polisher
            qa_result: Result from QA finalizer

        Returns:
            Complete presentation_ready dict
        """
        presentation_ready = {
            "widgets": polish_result.get("polished_content", widgets),
            "enhanced_widgets": polish_result.get("enhanced_content", widgets),
            "transition_suggestions": polish_result.get("transition_suggestions", []),
            "delivery_sequence": sequence_list,
            "flow_analysis": {
                "narrative_flow": flow_result.get("flow_analysis", "Coherent flow"),
                "flow_issues": flow_result.get("flow_issues", []),
                "pacing_analysis": flow_result.get(
                    "pacing_analysis", "Appropriate pacing"
                ),
                "pacing_issues": flow_result.get("pacing_issues", []),
            },
            "qa_report": {
                "quality_check": qa_result.get("quality_check", "passed"),
                "accessibility_check": qa_result.get("accessibility_check", "passed"),
                "format_check": qa_result.get("format_check", "passed"),
                "sequence_check": qa_result.get("sequence_check", "passed"),
                "all_passed": qa_result.get("all_passed", True),
                "issues": qa_result.get("issues", []),
            },
            "ready_to_send": qa_result.get("ready_to_send", True),
            "design_context": {
                "color_scheme": design_data.get("color_scheme", {}),
                "visual_hierarchy": design_data.get("visual_hierarchy", []),
            },
            "researched_data": researched_data,
        }

        # Add warnings if issues detected
        issues: List[str] = []
        issues.extend(flow_result.get("flow_issues", []))
        issues.extend(flow_result.get("pacing_issues", []))
        issues.extend(qa_result.get("issues", []))

        if issues:
            presentation_ready["warnings"] = issues
            presentation_ready["requires_review"] = True

        return presentation_ready

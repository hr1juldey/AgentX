# =============================================================================
# AGENTX Presenter - Polisher Module
# =============================================================================
# Polishes widget content for clarity and impact
# =============================================================================

import dspy


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

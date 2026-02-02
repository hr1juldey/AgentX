"""Designer agent for UI widget selection.

Server-driven UI pattern - selects widgets with state awareness.
"""

import dspy

from agentx.agent.dspy_signatures.main_signatures import DesignerSignature


class DesignerAgent(dspy.Module):
    """Designer agent for UI widget selection.

    Server-driven UI pattern from C007.
    """

    def __init__(self) -> None:
        """Initialize the designer agent."""
        super().__init__()
        self.design = dspy.Predict(DesignerSignature)

    def forward(
        self, query: str, response: str, existing_widgets: list[str]
    ) -> dspy.Prediction:
        """Select appropriate UI widget based on query and context.

        Args:
            query: User's question or request.
            response: Agent's response content.
            existing_widgets: List of already shown widget types.

        Returns:
            dspy.Prediction: Widget recommendation with type and props.
        """
        result = self.design(
            query=query, response=response, existing_widgets=existing_widgets
        )
        return dspy.Prediction(
            recommended_widget=result.recommended_widget,  # type: ignore[attr-defined]
            widget_props=result.widget_props,  # type: ignore[attr-defined]
        )

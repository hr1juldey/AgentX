# =============================================================================
# AGENTX Selector Tools
# =============================================================================
# DSPy modules for the WIDGET SELECTOR agent (What Widgets?)
# =============================================================================

import dspy


class WidgetMatcherModule(dspy.Module):
    """Matches widgets to query intent and data type.

    Has 3 signatures:
    - MatchByIntent: Match widgets based on user intent
    - MatchByData: Match widgets based on data characteristics
    - MatchByContext: Match widgets based on context
    """

    def __init__(self):
        super().__init__()
        self.match_intent = dspy.Predict("query, insights -> matching_widgets")
        self.match_data = dspy.Predict("data_type -> matching_widgets")
        self.match_context = dspy.Predict("device_context -> suitable_widgets")

    def forward(
        self,
        designed_data: dict,
        device_context: str = "desktop",
    ) -> dict:
        """Match widgets based on designed data."""
        query = designed_data.get("query", "")
        insights = designed_data.get("insights", [])
        data_type = designed_data.get("data_type", "general")

        intent_result = self.match_intent(query=query, insights=str(insights))
        data_result = self.match_data(data_type=data_type)
        context_result = self.match_context(device_context=device_context)

        # Combine results
        widgets_set = set()

        if hasattr(intent_result, "matching_widgets"):
            widgets_set.update(intent_result.matching_widgets.split(","))
        if hasattr(data_result, "matching_widgets"):
            widgets_set.update(data_result.matching_widgets.split(","))
        if hasattr(context_result, "suitable_widgets"):
            widgets_set.update(context_result.suitable_widgets.split(","))

        # Convert to list and clean
        widgets = [w.strip().lower() for w in widgets_set if w.strip()]

        return {
            "widgets": widgets,
            "rationale": f"Selected based on query intent: {query}, data type: {data_type}, device: {device_context}",
        }


class SuitabilityCheckerModule(dspy.Module):
    """Checks widget suitability for device and content.

    Has 2 signatures:
    - CheckDeviceFit: Check if widget fits device constraints
    - CheckContentFit: Check if widget fits content type
    """

    def __init__(self):
        super().__init__()
        self.check_device = dspy.Predict("widget, device -> is_suitable, reason")
        self.check_content = dspy.Predict("widget, content_type -> is_suitable, reason")

    def forward(
        self,
        widgets: list,
        device_context: str = "desktop",
    ) -> dict:
        """Check widget suitability."""
        suitable_widgets = []

        for widget in widgets:
            device_result = self.check_device(widget=widget, device=device_context)

            if (
                hasattr(device_result, "is_suitable")
                and device_result.is_suitable == "true"
            ):
                suitable_widgets.append(
                    {
                        "widget": widget,
                        "reason": device_result.reason
                        if hasattr(device_result, "reason")
                        else "",
                    }
                )

        return {
            "suitable_widgets": suitable_widgets,
            "device_context": device_context,
        }

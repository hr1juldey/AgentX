# =============================================================================
# AGENTX Designer - POV Generator Module
# =============================================================================
# Generates multiple points of view for balanced analysis
# =============================================================================

import dspy


class POVGeneratorModule(dspy.Module):
    """Generates multiple points of view for balanced analysis.

    Has 3 signatures:
    - GeneratePOVs: Generate bull/bear/neutral POVs
    - BalancePerspectives: Ensure balanced representation
    - AddNuance: Add nuanced considerations
    """

    def __init__(self):
        super().__init__()
        self.generate_povs = dspy.Predict("query, data -> points_of_view")
        self.balance_perspectives = dspy.Predict("points_of_view -> balanced_povs")
        self.add_nuance = dspy.Predict("povs -> nuanced_povs")

    def forward(self, query: str, researched_data: dict) -> dict:
        """Generate balanced POVs."""
        povs_result = self.generate_povs(query=query, data=str(researched_data))

        if hasattr(povs_result, "points_of_view"):
            balanced_result = self.balance_perspectives(
                points_of_view=povs_result.points_of_view
            )
            nuanced_result = self.add_nuance(povs=str(balanced_result))

            return {
                "points_of_view": [
                    pov.strip()
                    for pov in str(povs_result.points_of_view).split(",")
                    if pov.strip()
                ],
                "balanced_povs": balanced_result.balanced_povs
                if hasattr(balanced_result, "balanced_povs")
                else [],
                "nuanced_analysis": nuanced_result.nuanced_povs
                if hasattr(nuanced_result, "nuanced_povs")
                else "",
            }

        return {"points_of_view": [], "balanced_povs": [], "nuanced_analysis": ""}

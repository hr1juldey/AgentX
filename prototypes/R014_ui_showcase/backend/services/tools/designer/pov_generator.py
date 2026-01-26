# =============================================================================
# AGENTX Designer - POV Generator Module
# =============================================================================
# Generates multiple points of view for balanced analysis
# =============================================================================

import dspy
import json
import logging

from services.tools.hydrators.widget_signatures import POVGeneration

logger = logging.getLogger(__name__)


class POVGeneratorModule(dspy.Module):
    """Generates multiple balanced points of view with structured output.

    Has DSPy signature for proper POV generation with 3-5 perspectives.
    """

    def __init__(self):
        super().__init__()
        self.generate_povs = dspy.Predict(POVGeneration)

    def forward(self, query: str, researched_data: dict) -> dict:
        """Generate balanced POVs with structured output."""
        try:
            result = self.generate_povs(
                query=query,
                research_data=str(researched_data),
            )

            # Extract structured output
            povs_str = getattr(result, "points_of_view", "[]")

            # Parse POVs - expect JSON array
            try:
                if isinstance(povs_str, str):
                    # Try JSON parse first
                    povs = json.loads(povs_str)
                elif isinstance(povs_str, list):
                    povs = povs_str
                else:
                    # Fallback: comma-separated string
                    povs = [p.strip() for p in str(povs_str).split(",") if p.strip()]
            except (json.JSONDecodeError, TypeError):
                # Fallback to comma-separated
                povs = [p.strip() for p in str(povs_str).split(",") if p.strip()]

            # Ensure minimum 3 POVs
            if len(povs) < 3:
                logger.warning(f"Only {len(povs)} POVs generated, expected 3+")
                # Add default POVs if missing
                default_povs = [
                    f"Neutral: Analysis of {query}",
                    f"Optimistic: Positive outlook on {query}",
                    f"Cautious: Risk factors for {query}",
                ]
                povs.extend(default_povs[len(povs) :])

            return {
                "points_of_view": povs[:5],  # Max 5 POVs
                "pov_count": len(povs[:5]),
            }

        except Exception as e:
            logger.error(f"POV generator error: {e}")
            return {
                "points_of_view": [f"Neutral: {query}"],
                "pov_count": 1,
                "error": str(e),
            }

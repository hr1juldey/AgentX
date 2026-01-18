# =============================================================================
# AGENTX R013 - Itinerary Signature
# =============================================================================
# DSPy signature for itinerary planning
# =============================================================================

import dspy


class PlanItinerary(dspy.Signature):
    """Create day-by-day itinerary."""

    destination = dspy.InputField()
    days = dspy.InputField(desc="Number of days")
    interests = dspy.InputField()
    itinerary = dspy.OutputField(desc="Day-by-day plan")

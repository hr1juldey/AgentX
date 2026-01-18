# =============================================================================
# AGENTX R013 - Lodging Signature
# =============================================================================
# DSPy signature for lodging planning
# =============================================================================

import dspy


class PlanLodging(dspy.Signature):
    """Plan lodging options."""

    destination = dspy.InputField()
    budget = dspy.InputField()
    group_size = dspy.InputField()
    lodging_options = dspy.OutputField(desc="Available lodging with costs")

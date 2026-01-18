# =============================================================================
# AGENTX R013 - Transport Signature
# =============================================================================
# DSPy signature for transport planning
# =============================================================================

import dspy


class PlanTransport(dspy.Signature):
    """Plan transport options."""

    destination = dspy.InputField()
    budget = dspy.InputField()
    group_size = dspy.InputField()
    transport_options = dspy.OutputField(desc="Available transport with costs")

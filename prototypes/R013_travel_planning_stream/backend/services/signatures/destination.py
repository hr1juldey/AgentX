# =============================================================================
# AGENTX R013 - Destination Signatures
# =============================================================================
# DSPy signatures for destination discovery and information retrieval
# =============================================================================

import dspy


class DiscoverDestination(dspy.Signature):
    """Find best destinations based on user query."""

    question = dspy.InputField(desc="User's travel question")
    destination = dspy.OutputField(desc="Recommended destination with reasoning")


class GetDestinationInfo(dspy.Signature):
    """Get current information about destination."""

    destination = dspy.InputField(desc="Destination name")
    info = dspy.OutputField(desc="Current attractions, festivals, activities")

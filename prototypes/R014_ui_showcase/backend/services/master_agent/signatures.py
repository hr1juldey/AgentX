# =============================================================================
# AGENTX Master Agent Signatures
# =============================================================================
# DSPy signatures for Master Agent decision-making
# =============================================================================

import dspy


class MasterAgentSignature(dspy.Signature):
    """Master Agent signature for orchestrating all specialist agents."""

    user_query = dspy.InputField(desc="User query requesting information or action")
    device_context = dspy.InputField(
        desc="Device context for presentation (desktop/mobile)"
    )

    delivery_plan = dspy.OutputField(
        desc="Structured delivery plan with staggered timing"
    )
    widgets = dspy.OutputField(desc="List of hydrated widgets to deliver")
    qa_checklist = dspy.OutputField(desc="Quality assurance checkpoint results")

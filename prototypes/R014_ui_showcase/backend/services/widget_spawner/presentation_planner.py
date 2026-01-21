# =============================================================================
# AGENTX Widget Spawner - Presentation Planner Agent
# =============================================================================
# Plans multi-dimensional presentation using BestOfN pattern.
# Generates 5 options and selects the best using reward functions.
# =============================================================================

import json
import logging
from typing import Dict, Any

import dspy

from services.widget_spawner.layout_utils import generate_positions
from services.widget_spawner.reward_functions import presentation_quality_score

logger = logging.getLogger(__name__)


class PlanPresentationSignature(dspy.Signature):
    """Plan multi-dimensional presentation (widgets, layout, colors)."""
    content_analysis: str = dspy.InputField(desc="Content type, complexity")
    user_intent: str = dspy.InputField(desc="Goal: explore/compare/decide")
    device_context: str = dspy.InputField(desc="Mobile, desktop, tablet")
    presentation_plan: str = dspy.OutputField(desc="Complete UI spec in JSON")


class PresentationPlannerAgent(dspy.Module):
    """
    Presentation planner using BestOfN pattern.

    Generates N different presentation approaches and selects the best
    using the presentation_quality_score reward function.
    """

    def __init__(self, n: int = 5, threshold: float = 0.7):
        """
        Initialize the presentation planner.

        Args:
            n: Number of presentation options to generate (default: 5)
            threshold: Minimum quality score to accept (default: 0.7)
        """
        super().__init__()
        self.n = n
        self.threshold = threshold

        # Use BestOfN to generate multiple plans, select best
        self.planner = dspy.BestOfN(
            module=dspy.ChainOfThought(PlanPresentationSignature),
            N=n,
            reward_fn=presentation_quality_score,
            threshold=threshold
        )

    def forward(
        self,
        content_analysis: str,
        user_intent: str,
        device_context: Dict[str, Any]
    ) -> dspy.Prediction:
        """
        Generate presentation plan with BestOfN selection.

        Args:
            content_analysis: Content type analysis from ContextAnalyzer
            user_intent: User intent from ContextAnalyzer
            device_context: Device information

        Returns:
            dspy.Prediction with presentation_plan (JSON string)
        """
        logger.debug(
            f"📋 PresentationPlanner generating {self.n} options for: "
            f"{content_analysis}, intent: {user_intent}"
        )

        # Generate plan with BestOfN
        result = self.planner(
            content_analysis=content_analysis,
            user_intent=user_intent,
            device_context=json.dumps(device_context)
        )

        logger.debug(f"📋 BestOfN selected plan with score: {getattr(result, 'reward_score', 'N/A')}")

        # Add optional positions to the selected plan
        try:
            plan = json.loads(result.presentation_plan)
            positioned_plan = generate_positions(plan, device_context)

            logger.debug(f"📋 Positioned {len(positioned_plan['widgets'])} widgets for layout: {plan.get('layout')}")

            return dspy.Prediction(
                presentation_plan=json.dumps(positioned_plan),
                raw_plan=result.presentation_plan,
                reward_score=getattr(result, "reward_score", None)
            )
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"📋 Failed to process plan: {e}")
            return result

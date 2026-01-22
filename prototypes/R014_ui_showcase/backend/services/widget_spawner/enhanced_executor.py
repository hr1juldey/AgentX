# =============================================================================
# AGENTX Widget Spawner - Enhanced Content Generator
# =============================================================================
# Generates high-quality widgets using Refine pattern for self-improvement.
# Iteratively improves accessibility until threshold is met.
# =============================================================================

import json
import logging
from typing import Dict, Any

import dspy

from services.widget_spawner.reward_functions import accessibility_compliance_score

logger = logging.getLogger(__name__)


class GenerateWidgetSignature(dspy.Signature):
    """Generate widget content with design system constraints."""

    widget_spec: str = dspy.InputField(desc="Widget type, context, requirements")
    design_system: str = dspy.InputField(desc="Colors, typography")
    widget_content: str = dspy.OutputField(desc="Generated widget content")
    accessibility_score: float = dspy.OutputField(desc="Self-assessed accessibility")


class EnhancedExecutorAgent(dspy.Module):
    """
    Enhanced content generator using Refine pattern.

    Self-improves accessibility compliance through iterative refinement.
    Tries up to N times to achieve the accessibility threshold.
    """

    def __init__(self, n: int = 3, threshold: float = 0.95):
        """
        Initialize the enhanced executor.

        Args:
            n: Maximum number of refinement attempts (default: 3)
            threshold: Target accessibility score (default: 0.95 for WCAG AA)
        """
        super().__init__()
        self.n = n
        self.threshold = threshold

        # Use Refine to self-improve accessibility
        self.generator = dspy.Refine(
            module=dspy.ChainOfThought(GenerateWidgetSignature),
            N=n,
            reward_fn=accessibility_compliance_score,
            threshold=threshold,
        )

    def forward(
        self,
        widget_spec: Dict[str, Any],
        design_system: Dict[str, Any],
        accessibility_requirements: str = "WCAG_AA",
    ) -> dspy.Prediction:
        """
        Generate widget content with self-improving accessibility.

        Args:
            widget_spec: Widget specification (type, context, requirements)
            design_system: Design system (colors, typography)
            accessibility_requirements: WCAG level to target

        Returns:
            dspy.Prediction with widget_content and accessibility_score
        """
        logger.debug(
            f"🎨 EnhancedExecutor generating {widget_spec.get('type')} widget "
            f"with {self.n} refinement attempts"
        )

        result = self.generator(
            widget_spec=json.dumps(widget_spec), design_system=json.dumps(design_system)
        )

        logger.debug(
            f"🎨 Generated widget with accessibility score: "
            f"{getattr(result, 'accessibility_score', 'N/A')}"
        )

        return result

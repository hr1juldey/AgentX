"""DSPy EvaluateProgressModule for progress evaluation.

This module defines the DSPy signature and module for evaluating
accumulated research findings and deciding whether to continue.
"""

import dspy

from agentx.domain.models.routing import (
    ContinuationAction,
    ContinuationDecision,
)


class EvaluateProgressSignature(dspy.Signature):
    """Signature for evaluating research progress.

    The LLM evaluates accumulated state and decides:
    1. Do I have enough to answer? (continue_research vs finalize)
    2. What's still missing? (missing_information)
    3. How confident am I? (confidence 0.0-1.0)

    Key insight: Uses STRUCTURED OUTPUT (not text parsing).
    """

    original_query = dspy.InputField(desc="User's original query")
    accumulated_findings = dspy.InputField(desc="All research gathered so far")
    accumulated_confidence = dspy.InputField(
        desc="Current confidence score (0.0-1.0)",
    )
    information_gaps = dspy.InputField(desc="What's still missing (list)")
    current_iteration = dspy.InputField(desc="Iteration number (1-based)")

    action = dspy.OutputField(
        desc="Action: continue_research, finalize, or add_tasks",
    )
    confidence = dspy.OutputField(
        desc="LLM's confidence in current information (0.0-1.0 as float)",
    )
    missing_information = dspy.OutputField(
        desc="JSON string of what's still needed: ['gap1', 'gap2']",
    )
    reasoning = dspy.OutputField(
        desc="Why this action was chosen",
    )


class EvaluateProgressModule(dspy.Module):
    """DSPy module for evaluating research progress.

    This module evaluates the accumulated research findings and decides
    whether to continue research, finalize the response, or add more tasks.

    The evaluator uses STRUCTURED OUTPUT (not text parsing) to avoid
    the R014 bug where text parsing fails.
    """

    def __init__(self):
        """Initialize the evaluator module."""
        super().__init__()
        self.evaluate = dspy.Predict(EvaluateProgressSignature)

    def forward(
        self,
        original_query: str,
        accumulated_findings: list[str],
        accumulated_confidence: float,
        information_gaps: list[str],
        current_iteration: int,
    ) -> dspy.Prediction:
        """Evaluate research progress and recommend next action.

        Args:
            original_query: User's original query
            accumulated_findings: All research gathered so far
            accumulated_confidence: Current confidence score
            information_gaps: Known information gaps
            current_iteration: Current iteration number

        Returns:
            dspy.Prediction: Contains ContinuationDecision
        """
        # Format findings and gaps for LLM
        findings_text = "\n".join(f"- {f}" for f in accumulated_findings)
        gaps_text = (
            "\n".join(f"- {g}" for g in information_gaps)
            if information_gaps
            else "None"
        )

        # Evaluate using LLM
        result = self.evaluate(
            original_query=original_query,
            accumulated_findings=findings_text,
            accumulated_confidence=str(accumulated_confidence),
            information_gaps=gaps_text,
            current_iteration=str(current_iteration),
        )

        # Parse action (enum validation)
        try:
            action = ContinuationAction(result.action.strip().lower())  # type: ignore[attr-defined]
        except ValueError:
            # Default to finalize if invalid action
            action = ContinuationAction.FINALIZE

        # Parse confidence
        try:
            confidence = float(result.confidence)  # type: ignore[attr-defined]
            confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
        except ValueError:
            confidence = accumulated_confidence  # Use existing confidence

        # Parse missing information
        import json

        missing: list[str] = []
        try:
            missing = json.loads(result.missing_information)  # type: ignore[attr-defined]
        except (json.JSONDecodeError, ValueError):
            if result.missing_information:  # type: ignore[attr-defined]
                missing = [result.missing_information]  # type: ignore[attr-defined]

        # Create continuation decision
        decision = ContinuationDecision(
            action=action,
            confidence=confidence,
            missing_information=missing,
            reasoning=result.reasoning,  # type: ignore[attr-defined]
        )

        return dspy.Prediction(
            decision=decision,
        )

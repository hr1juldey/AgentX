"""Evaluator node for the dynamic agent graph.

This node evaluates accumulated research findings and decides
whether to continue research or finalize the response.
"""

from agentx.agent.tools.evaluator.evaluate_progress import EvaluateProgressModule
from agentx.domain.models.graph_state import AgentState
from agentx.domain.models.routing import ContinuationDecision


def evaluator_node(state: AgentState) -> dict:
    """Evaluate research progress and decide next action.

    This node uses the EvaluateProgressModule to analyze accumulated
    findings and decide whether to continue research or finalize.

    Args:
        state: Current agent state

    Returns:
        dict: Updated state with continuation_decision and confidence
    """
    # Get accumulated state
    original_query = state["query"]
    findings = state.get("research_findings", [])
    gaps = state.get("information_gaps", [])
    current_confidence = state.get("accumulated_confidence", 0.0)
    iteration = state.get("current_iteration", 0)

    # Initialize evaluator module
    evaluator = EvaluateProgressModule()

    # Evaluate progress
    prediction = evaluator(
        original_query=original_query,
        accumulated_findings=findings,
        accumulated_confidence=current_confidence,
        information_gaps=gaps,
        current_iteration=iteration + 1,  # 1-based for LLM
    )

    decision: ContinuationDecision = prediction.decision  # type: ignore[attr-defined]

    # Update accumulated confidence (max of old and new)
    new_confidence = max(current_confidence, decision.confidence)

    # Update information gaps with LLM's assessment
    updated_gaps = list(set(gaps + decision.missing_information))

    return {
        "continuation_decision": decision,
        "accumulated_confidence": new_confidence,
        "information_gaps": updated_gaps,
        "research_quality": decision.reasoning,
        "execution_path": ["evaluator"],
    }


def should_continue_research(state: AgentState) -> str:
    """Route based on evaluator's decision.

    Args:
        state: Current agent state

    Returns:
        str: Routing path ("continue", "add_tasks", or "finalize")
    """
    decision = state.get("continuation_decision")
    if not decision:
        return "finalize"

    # Max iterations safety check
    max_iterations = 5
    iteration = state.get("current_iteration", 0)

    if iteration >= max_iterations:
        return "finalize"

    # Route based on decision action
    action = decision.action  # type: ignore[attr-defined]
    if action == "continue_research":
        return "continue"
    elif action == "add_tasks":
        return "add_tasks"
    else:
        return "finalize"

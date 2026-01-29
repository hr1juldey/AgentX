"""Presenter node for LangGraph.

Ported from R014: services/pipeline/presenter.py

Presents findings in polished format and performs quality check.
Final node in the 7-pipeline agent sequence.
"""

from typing import Any

from langchain_core.messages import AIMessage

from agentx.agent.dspy_signatures.pipeline.presenter import (
    PresentFindings,
    QualityCheck,
)
from agentx.agent.state import AgentState
from agentx.agent.tools.common.dspy_helpers import safe_extract
from agentx.agent.tools.common.type_utils import _to_float, _to_bool
import dspy


async def presenter_node(state: AgentState) -> dict[str, Any]:
    """Presenter node: Present findings with quality check.

    Coordinates:
    - Findings presentation (polished format)
    - Quality check (validation)

    Args:
        state: Current agent state

    Returns:
        Updated state with final presentation
    """
    # Get contextualized findings
    contextualized: dict[str, object] = state.get("contextualized_data", {})  # type: ignore[assignment]
    findings = str(contextualized.get("findings", ""))

    if not findings:
        return {
            "messages": [AIMessage(content="No findings to present.")],
            "total_tool_calls": state.get("total_tool_calls", 0),
        }

    # Get user query
    messages = state["messages"]
    user_query: str = ""
    for msg in reversed(messages):
        if hasattr(msg, "content") and isinstance(msg.content, str):
            user_query = msg.content
            break

    # Initialize DSPy modules
    presenter = dspy.Predict(PresentFindings)
    qa_checker = dspy.Predict(QualityCheck)

    # Step 1: Generate presentation
    presentation_result = presenter(
        raw_findings=findings,
        query=user_query,
    )

    presentation = safe_extract(presentation_result, "presentation", "")

    # Step 2: Quality check
    qa_result = qa_checker(
        presentation=presentation,
        query=user_query,
    )

    quality_score = _to_float(
        safe_extract(qa_result, "quality_score", 0.5), default=0.5
    )
    issues = safe_extract(qa_result, "issues", "")
    approved = _to_bool(safe_extract(qa_result, "approved", True), default=True)

    # Create presenter message
    presenter_content = f"""Final Presentation:

{presentation}

---
Quality Check:
Quality Score: {quality_score:.2f}
Status: {"APPROVED" if approved else "NEEDS REVIEW"}
{f"Issues: {issues}" if issues else "No issues found"}
"""

    message = AIMessage(content=presenter_content)

    return {
        "messages": [message],
        "_final_presentation": {
            "presentation": presentation,
            "quality_score": quality_score,
            "approved": approved,
            "issues": issues,
        },
        "total_tool_calls": state.get("total_tool_calls", 0) + 1,
    }

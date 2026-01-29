"""Widget Selector node for LangGraph.

Ported from R014: services/pipeline/widget_selector.py

Hybrid rule-based + LLM widget selection.
Uses rule-based selector for fast path, falls back to LLM for complex cases.
"""

from typing import Any

from langchain_core.messages import AIMessage

from agentx.agent.agents.rule_based_selector import RuleBasedWidgetSelector
from agentx.agent.agents.widget_matcher import WidgetMatcherModule
from agentx.agent.state import AgentState


async def widget_selector_node(state: AgentState) -> dict[str, Any]:
    """Widget Selector node: Select appropriate UI widget.

    Hybrid approach:
    - Pass 1: Rule-based selector (fast path for common patterns)
    - Pass 2: LLM-based matcher (for complex cases)

    Args:
        state: Current agent state

    Returns:
        Updated state with selected widget
    """
    # Get widget design from designer
    widget_design: dict[str, object] = state.get("_widget_design", {})  # type: ignore[assignment]

    # Get existing widgets
    existing_widgets = list(widget_design.get("existing_widgets", []))  # type: ignore[arg-type]

    # Get user query
    messages = state["messages"]
    user_query: str = ""
    for msg in reversed(messages):
        if hasattr(msg, "content") and isinstance(msg.content, str):
            user_query = msg.content
            break

    # Get findings for content type detection
    contextualized: dict[str, object] = state.get("contextualized_data", {})  # type: ignore[assignment]
    findings = str(contextualized.get("findings", ""))

    # Detect content type
    content_type = _detect_content_type(findings)

    # Initialize selectors
    rule_selector = RuleBasedWidgetSelector()
    llm_matcher = WidgetMatcherModule()

    # Step 1: Try rule-based selection (fast path)
    rule_result = rule_selector.select(
        query=user_query,
        content_type=content_type,
        existing_widgets=existing_widgets,
    )

    if rule_result:
        # Rule-based selection succeeded
        selected_widget = rule_result["widget"]
        confidence = rule_result["confidence"]
        reasoning = rule_result["reasoning"]
        selection_method = "rule-based"
    else:
        # Step 2: Fall back to LLM-based matcher
        content_summary = findings[:200] + "..." if len(findings) > 200 else findings

        llm_result = llm_matcher.forward(
            query=user_query,
            content_type=content_type,
            content_summary=content_summary,
            existing_widgets=existing_widgets,
        )

        selected_widget = llm_result["selected_widget"]
        confidence = llm_result["confidence"]
        reasoning = llm_result["reasoning"]
        selection_method = "LLM-based"

    # Create selection message
    selection_content = f"""Widget Selection:

Selected Widget: {selected_widget}
Confidence: {confidence:.2f}
Selection Method: {selection_method}

Reasoning:
{reasoning}

Existing Widgets: {", ".join(existing_widgets) if existing_widgets else "none"}

This widget was selected to complement the existing UI without duplication.
"""

    message = AIMessage(content=selection_content)

    return {
        "messages": [message],
        "_widget_selection": {
            "widget_type": selected_widget,
            "confidence": confidence,
            "reasoning": reasoning,
            "selection_method": selection_method,
            "existing_widgets": existing_widgets,
        },
        "total_tool_calls": state.get("total_tool_calls", 0) + 1,
    }


def _detect_content_type(findings: str) -> str:
    """Detect content type from findings text.

    Args:
        findings: Research findings text

    Returns:
        str: Content type (text, data, image, etc.)
    """
    findings_lower = findings.lower()

    # Check for data visualization patterns
    data_keywords = {"chart", "graph", "data", "statistics", "metrics", "trend"}
    if any(kw in findings_lower for kw in data_keywords):
        return "data"

    # Check for image references
    image_keywords = {"image", "picture", "photo", "screenshot", "figure"}
    if any(kw in findings_lower for kw in image_keywords):
        return "image"

    # Default to text
    return "text"

# =============================================================================
# AGENTX Calendar - Agent (Infrastructure Layer)
# =============================================================================
# DSPy ReAct module for complex date/time queries
# =============================================================================
# ReAct is used instead of CodeAct for better compatibility with smaller LLMs
# like qwen3:8b that don't reliably output strict JSON formatting.
# =============================================================================

import dspy

from services.tools.calendar.signature import CalendarQuery
from services.tools.calendar.tools import (
    add_weekdays,
    calculate_date_offset,
    days_between_dates,
    get_current_datetime,
    get_day_of_week,
    is_weekend,
)


def _wrap_tool(tool_func, name: str):
    """Wrap a tool function for DSPy ReAct compatibility.

    ReAct requires tools with proper docstrings for function calling.
    """

    def wrapped(*args, **kwargs):
        return tool_func(*args, **kwargs)

    wrapped.__name__ = name
    wrapped.__doc__ = tool_func.__doc__
    return wrapped


class CalendarAgent(dspy.Module):
    """Calendar agent using ReAct for time-aware queries.

    Uses DSPy ReAct (reasoning + acting) for date/time calculations.
    ReAct is more flexible than CodeAct for smaller LLMs like qwen3:8b.

    Examples:
        "Was it a Monday on September 27, 1999?"
        "What is the date 30 days from now?"
        "How many days until Christmas?"
    """

    def __init__(self, max_iters: int = 5):
        super().__init__()

        # Wrap tools with proper names for ReAct
        tools = [
            _wrap_tool(get_current_datetime, "get_current_datetime"),
            _wrap_tool(get_day_of_week, "get_day_of_week"),
            _wrap_tool(calculate_date_offset, "calculate_date_offset"),
            _wrap_tool(days_between_dates, "days_between_dates"),
            _wrap_tool(is_weekend, "is_weekend"),
            _wrap_tool(add_weekdays, "add_weekdays"),
        ]

        # Use ReAct instead of CodeAct for better qwen3:8b compatibility
        self.react = dspy.ReAct(
            signature=CalendarQuery,
            tools=tools,
            max_iters=max_iters,
        )

    def forward(self, question: str) -> dict:
        """Process a time-related question.

        Args:
            question: Natural language question about dates/times

        Returns:
            Dict with answer and execution trajectory
        """
        result = self.react(question=question)

        # Extract answer from ReAct result
        answer = result.answer if hasattr(result, "answer") else ""

        # Extract trajectory (shows which tools were called)
        trajectory = []
        if hasattr(result, "trajectory") and result.trajectory:
            for step in result.trajectory:
                if hasattr(step, "tool"):
                    trajectory.append(
                        {
                            "tool": getattr(step, "tool", "unknown"),
                            "observation": str(getattr(step, "observation", ""))[:100],
                        }
                    )

        return {
            "answer": answer,
            "trajectory": trajectory,
        }

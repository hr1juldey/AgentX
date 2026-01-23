# =============================================================================
# AGENTX Calendar - Public API
# =============================================================================

# Simple: Direct function access (fast, no LLM)
from services.tools.calendar.tools import (
    add_weekdays,
    calculate_date_offset,
    days_between_dates,
    get_current_datetime,
    get_day_of_week,
    is_weekend,
)

# Complex: Agent access (CodeAct for natural language)
from services.tools.calendar.agent import CalendarAgent

__all__ = [
    # Simple functions
    "get_current_datetime",
    "get_day_of_week",
    "calculate_date_offset",
    "days_between_dates",
    "is_weekend",
    "add_weekdays",
    # Agent
    "CalendarAgent",
]

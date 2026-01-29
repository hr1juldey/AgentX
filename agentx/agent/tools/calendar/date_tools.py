"""Date and calendar utilities for agent tools.

Simple date/time utilities for agent operations.
Not a complex calendar agent - just utilities for date calculations.
"""

from datetime import date, timedelta
from typing import Optional


def get_current_date() -> str:
    """Get current date in ISO format.

    Returns:
        Current date as YYYY-MM-DD string
    """
    return date.today().isoformat()


def calculate_date_offset(
    base_date: Optional[str] = None,
    days_offset: int = 0,
) -> str:
    """Calculate date with offset from base date.

    Args:
        base_date: Base date in ISO format (YYYY-MM-DD). Defaults to today.
        days_offset: Number of days to offset (positive for future, negative for past)

    Returns:
        Calculated date as YYYY-MM-DD string
    """
    if base_date is None:
        base = date.today()
    else:
        base = date.fromisoformat(base_date)

    result = base + timedelta(days=days_offset)
    return result.isoformat()


def day_of_week(input_date: Optional[str] = None) -> str:
    """Get day of week for a date.

    Args:
        input_date: Date in ISO format (YYYY-MM-DD). Defaults to today.

    Returns:
        Day of week (Monday, Tuesday, etc.)
    """
    if input_date is None:
        target = date.today()
    else:
        target = date.fromisoformat(input_date)

    return target.strftime("%A")


def date_difference(
    date1: str,
    date2: str,
) -> int:
    """Calculate difference in days between two dates.

    Args:
        date1: First date in ISO format (YYYY-MM-DD)
        date2: Second date in ISO format (YYYY-MM-DD)

    Returns:
        Number of days difference (absolute value)
    """
    d1 = date.fromisoformat(date1)
    d2 = date.fromisoformat(date2)
    return abs((d2 - d1).days)


def is_weekend(input_date: Optional[str] = None) -> bool:
    """Check if a date falls on a weekend.

    Args:
        input_date: Date in ISO format (YYYY-MM-DD). Defaults to today.

    Returns:
        True if date is Saturday or Sunday
    """
    if input_date is None:
        target = date.today()
    else:
        target = date.fromisoformat(input_date)

    return target.weekday() >= 5  # 5=Saturday, 6=Sunday

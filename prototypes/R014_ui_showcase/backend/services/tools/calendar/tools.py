# =============================================================================
# AGENTX Calendar - Tools (Domain Layer)
# =============================================================================
# Pure date/time calculation functions
# =============================================================================
# IMPORTANT: For CodeAct compatibility, all imports must be inside functions
# =============================================================================


def get_current_datetime(format_type: str = "datetime") -> str:
    """Get current date/time in specified format.

    Args:
        format_type: One of 'date', 'time', or 'datetime'

    Returns:
        Current date/time formatted string
    """
    from datetime import datetime

    now = datetime.now()

    formats = {
        "date": "%Y-%m-%d",
        "time": "%H:%M:%S",
        "datetime": "%Y-%m-%d %H:%M:%S",
    }

    fmt = formats.get(format_type, "%Y-%m-%d %H:%M:%S")
    return now.strftime(fmt)


def get_day_of_week(date_string: str) -> str:
    """Get the day of the week for a given date.

    Args:
        date_string: Date in YYYY-MM-DD format

    Returns:
        Day name: Monday, Tuesday, Wednesday, etc.
    """
    from datetime import datetime

    date_obj = datetime.strptime(date_string, "%Y-%m-%d")
    return date_obj.strftime("%A")


def calculate_date_offset(base_date: str, days: int) -> str:
    """Calculate date with day offset from base date.

    Args:
        base_date: Base date in YYYY-MM-DD format
        days: Day offset (positive for future, negative for past)

    Returns:
        Calculated date in YYYY-MM-DD format
    """
    from datetime import datetime, timedelta

    date_obj = datetime.strptime(base_date, "%Y-%m-%d")
    result = date_obj + timedelta(days=days)
    return result.strftime("%Y-%m-%d")


def days_between_dates(date1: str, date2: str) -> int:
    """Calculate the number of days between two dates.

    Args:
        date1: First date in YYYY-MM-DD format
        date2: Second date in YYYY-MM-DD format

    Returns:
        Number of days between dates (absolute value)
    """
    from datetime import datetime

    d1 = datetime.strptime(date1, "%Y-%m-%d")
    d2 = datetime.strptime(date2, "%Y-%m-%d")
    return abs((d2 - d1).days)


def is_weekend(date_string: str) -> bool:
    """Check if a given date is a weekend.

    Args:
        date_string: Date in YYYY-MM-DD format

    Returns:
        True if Saturday or Sunday, False otherwise
    """
    from datetime import datetime

    date_obj = datetime.strptime(date_string, "%Y-%m-%d")
    return date_obj.weekday() >= 5


def add_weekdays(base_date: str, weekdays: int) -> str:
    """Add weekdays to a date (skipping weekends).

    Args:
        base_date: Base date in YYYY-MM-DD format
        weekdays: Number of weekdays to add (can be negative)

    Returns:
        Resulting date in YYYY-MM-DD format
    """
    from datetime import datetime, timedelta

    date_obj = datetime.strptime(base_date, "%Y-%m-%d")
    days_added = 0
    result = date_obj

    while days_added < abs(weekdays):
        result = result + timedelta(days=1 if weekdays > 0 else -1)
        if result.weekday() < 5:  # Monday=0, Friday=4
            days_added += 1

    return result.strftime("%Y-%m-%d")

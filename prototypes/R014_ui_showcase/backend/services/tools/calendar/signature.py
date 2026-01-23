# =============================================================================
# AGENTX Calendar - DSPy Signatures
# =============================================================================
# Input/output contracts for calendar operations
# =============================================================================

import dspy


class CalendarQuery(dspy.Signature):
    """Answer time-related questions using the available tools.

    AVAILABLE TOOLS (use these by name, don't write Python code):

    1. get_current_datetime(format_type)
       - Returns current date/time as string
       - format_type: 'date', 'time', or 'datetime'
       - Example: "2025-01-23 14:30:45"

    2. get_day_of_week(date_string)
       - Returns day name (Monday, Tuesday, etc.)
       - date_string: Date in YYYY-MM-DD format
       - Example: get_day_of_week("2000-01-01") → "Saturday"

    3. calculate_date_offset(base_date, days)
       - Returns date offset by N days from base
       - base_date: YYYY-MM-DD format
       - days: Integer (positive for future, negative for past)
       - Example: calculate_date_offset("2025-01-23", 7) → "2025-01-30"

    4. days_between_dates(date1, date2)
       - Returns number of days between two dates (absolute)
       - Both dates in YYYY-MM-DD format
       - Example: days_between_dates("2025-01-01", "2025-01-31") → 30

    5. is_weekend(date_string)
       - Returns True if date is Saturday/Sunday, False otherwise
       - date_string: YYYY-MM-DD format

    6. add_weekdays(base_date, weekdays)
       - Adds business days (skips weekends)
       - base_date: YYYY-MM-DD format
       - weekdays: Number of weekdays to add

    IMPORTANT: Think step by step about which tools to call and in what order.
    Call tools by name, then use the results to formulate your final answer.

    Examples:
        "Was it a Monday on September 27, 1999?"
        → Call get_day_of_week("1999-09-27")

        "What is the date 7 days from now?"
        → Call get_current_datetime("date"), then calculate_date_offset(result, 7)

        "How many days until Christmas?"
        → Call get_current_datetime("date"), then days_between_dates(result, "2025-12-25")
    """

    question: str = dspy.InputField(
        desc="Natural language question about dates or times"
    )
    answer: str = dspy.OutputField(desc="Answer to the time-related question")

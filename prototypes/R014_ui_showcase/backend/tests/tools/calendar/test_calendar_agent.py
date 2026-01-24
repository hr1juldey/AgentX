#!/usr/bin/env python3
"""
Standalone tests for CalendarAgent.
Tests CodeAct-based date/time queries with various complexity levels.
"""

import sys
from pathlib import Path

# Add backend to path (3 levels up from tests/tools/calendar/)
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

# Configure DSPy with Ollama BEFORE importing modules
import dspy

lm = dspy.LM(
    "ollama_chat/qwen3:8b",
    api_base="http://localhost:11434",
    api_key="",
)
dspy.configure(lm=lm)

from services.tools.calendar.agent import CalendarAgent


def test_calendar_basic_queries():
    """Test basic date/time queries."""
    print("\n=== Test: Calendar Agent - Basic Queries ===")

    agent = CalendarAgent()

    basic_queries = [
        "What day is it today?",
        "What is the current date and time?",
        "What month are we in?",
        "What year is it?",
    ]

    for query in basic_queries:
        print(f"\n  Query: '{query}'")
        result = agent(question=query)
        answer = result.get("answer", "")
        trajectory = result.get("trajectory", {})

        print(f"    Answer: {answer}")
        print(f"    Trajectory steps: {len(trajectory)}")

        # Verify
        assert isinstance(result, dict), "Result should be a dict"
        assert "answer" in result, "Missing answer key"
        assert answer, "Answer should not be empty"


def test_calendar_day_of_week():
    """Test day-of-week queries for specific dates."""
    print("\n=== Test: Calendar Agent - Day of Week ===")

    agent = CalendarAgent()

    dow_queries = [
        ("What day of the week was January 1, 2000?", "Saturday"),
        ("Was it a Monday on September 27, 1999?", "Monday"),
        ("What day is Christmas 2025?", "Thursday"),
        ("What day of week was July 4, 1776?", "Thursday"),
    ]

    for query, expected_hint in dow_queries:
        print(f"\n  Query: '{query}'")
        result = agent(question=query)
        answer = result.get("answer", "")

        print(f"    Answer: {answer}")
        print(f"    Expected hint: {expected_hint}")

        # Check if answer contains the day (case-insensitive)
        assert expected_hint.lower() in answer.lower(), (
            f"Answer should mention {expected_hint}"
        )


def test_calendar_date_calculations():
    """Test date offset calculations."""
    print("\n=== Test: Calendar Agent - Date Calculations ===")

    agent = CalendarAgent()

    calc_queries = [
        "What is the date 7 days from now?",
        "What was the date 30 days ago?",
        "What is the date 100 days from today?",
        "What will be the date 1 year from now?",
    ]

    for query in calc_queries:
        print(f"\n  Query: '{query}'")
        result = agent(question=query)
        answer = result.get("answer", "")

        print(f"    Answer: {answer}")

        # Verify answer contains a date format
        assert any(char.isdigit() for char in answer), (
            "Answer should contain numbers/date"
        )


def test_calendar_date_differences():
    """Test days-between-dates calculations."""
    print("\n=== Test: Calendar Agent - Date Differences ===")

    agent = CalendarAgent()

    diff_queries = [
        "How many days until Christmas?",
        "How many days between January 1 and December 31, 2024?",
        "How many days since New Year's Day 2025?",
        "How many weeks until next year?",
    ]

    for query in diff_queries:
        print(f"\n  Query: '{query}'")
        result = agent(question=query)
        answer = result.get("answer", "")

        print(f"    Answer: {answer}")

        # Verify answer contains a number
        assert any(char.isdigit() for char in answer), "Answer should contain a number"


def test_calendar_weekend_queries():
    """Test weekend-related queries."""
    print("\n=== Test: Calendar Agent - Weekend Queries ===")

    agent = CalendarAgent()

    weekend_queries = [
        "Is today a weekend?",
        "Is next Saturday a weekend?",
        "How many weekends until the end of the year?",
        "What are the weekend dates next month?",
    ]

    for query in weekend_queries:
        print(f"\n  Query: '{query}'")
        result = agent(question=query)
        answer = result.get("answer", "")

        print(f"    Answer: {answer}")

        # Verify
        assert answer, "Answer should not be empty"


def test_calendar_complex_queries():
    """Test complex multi-step date/time queries."""
    print("\n=== Test: Calendar Agent - Complex Queries ===")

    agent = CalendarAgent()

    complex_queries = [
        "What is the date 3 weeks and 2 days from today?",
        "How many weekdays until my birthday if it's on December 25?",
        "What day of the week will it be 1000 days from now?",
        "If today is Monday, what day will it be 100 days from now?",
    ]

    for query in complex_queries:
        print(f"\n  Query: '{query}'")
        result = agent(question=query)
        answer = result.get("answer", "")

        print(f"    Answer: {answer}")

        # Verify
        assert answer, "Answer should not be empty"


def test_calendar_edge_cases():
    """Test edge cases and error handling."""
    print("\n=== Test: Calendar Agent - Edge Cases ===")

    agent = CalendarAgent()

    edge_cases = [
        "What is the date 0 days from now?",
        "How many days between today and today?",
        "What day was January 1, year 0?",  # Invalid year
        "What is the date -5 days from now?",  # Negative offset
    ]

    for query in edge_cases:
        print(f"\n  Query: '{query}'")
        try:
            result = agent(question=query)
            answer = result.get("answer", "")
            print(f"    Answer: {answer}")
        except Exception as e:
            print(f"    Error (expected for some): {e}")


def test_calendar_tool_trajectory():
    """Test that CodeAct uses the provided tools."""
    print("\n=== Test: Calendar Agent - Tool Trajectory ===")

    agent = CalendarAgent()

    # Query that requires multiple tools
    query = "How many days until next Saturday?"

    print(f"  Query: '{query}'")
    result = agent(question=query)
    trajectory = result.get("trajectory", [])

    print(f"  Trajectory steps: {len(trajectory)}")

    # Show trajectory
    for i, step in enumerate(trajectory, 1):
        tool_name = step.get("tool", "unknown")
        print(f"    Step {i}: Used tool '{tool_name}'")

    # Verify trajectory was recorded
    assert isinstance(trajectory, list), "Trajectory should be a list"


def test_calendar_real_world_scenarios():
    """Test real-world use case scenarios."""
    print("\n=== Test: Calendar Agent - Real-World Scenarios ===")

    agent = CalendarAgent()

    scenarios = [
        # Project planning
        "If a project starts on Monday and takes 15 business days, when does it end?",
        # Event planning
        "I need to plan a meeting 2 weeks from Friday. What date is that?",
        # Birthday calculation
        "I was born on March 15, 1990. How many days old am I?",
        # Holiday planning
        "Thanksgiving is on the fourth Thursday of November. What date is that in 2025?",
        # Countdown
        "How many days until January 1, 2030?",
    ]

    titles = [
        "Project Planning (15 business days)",
        "Event Planning (2 weeks from Friday)",
        "Age Calculation",
        "Thanksgiving 2025",
        "Countdown to 2030",
    ]

    for query, title in zip(scenarios, titles):
        print(f"\n  {title}:")
        print(f"    Query: '{query}'")
        result = agent(question=query)
        answer = result.get("answer", "")
        print(f"    Answer: {answer[:100]}...")

        # Verify
        assert answer, f"{title}: Should return an answer"


def run_all_calendar_tests():
    """Run all CalendarAgent tests."""
    print("=" * 60)
    print("CALENDAR AGENT TEST SUITE")
    print("=" * 60)
    print("Using model: ollama_chat/qwen3:8b")
    print("Agent: CodeAct with date/time tools")

    tests = [
        test_calendar_basic_queries,
        test_calendar_day_of_week,
        test_calendar_date_calculations,
        test_calendar_date_differences,
        test_calendar_weekend_queries,
        test_calendar_complex_queries,
        test_calendar_edge_cases,
        test_calendar_tool_trajectory,
        test_calendar_real_world_scenarios,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_calendar_tests()
    sys.exit(0 if success else 1)

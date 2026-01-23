#!/usr/bin/env python3
"""
Standalone tests for Selector tools and Pipeline agents.
Tests WidgetMatcherModule and WidgetSelectorAgent with complex scenarios.
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

# Configure DSPy with Ollama BEFORE importing modules
import dspy

lm = dspy.LM(
    "ollama_chat/qwen3:8b",
    api_base="http://localhost:11434",
    api_key="",
)
dspy.configure(lm=lm)

from services.tools.selector_tools import WidgetMatcherModule
from services.pipeline.widget_selector import WidgetSelectorAgent


def test_widget_matcher_basic():
    """Test basic widget matching with clear semantic patterns."""
    print("\n=== Test: Widget Matcher - Basic Semantic Patterns ===")

    module = WidgetMatcherModule()

    test_cases = [
        {
            "query": "Show real-time stock prices for AAPL",
            "data_type": "numerical_time_series",
            "device_context": "desktop",
            "expected_widget": "chart",
        },
        {
            "query": "Display photo gallery from my vacation",
            "data_type": "visual_image",
            "device_context": "desktop",
            "expected_widget": "gallery",
        },
        {
            "query": "Compare pricing plans for three subscription tiers",
            "data_type": "comparative",
            "device_context": "desktop",
            "expected_widget": "card",
        },
        {
            "query": "Create a user registration form wizard",
            "data_type": "general",
            "device_context": "desktop",
            "expected_widget": "form",
        },
        {
            "query": "Show current time in Tokyo",
            "data_type": "temporal",
            "device_context": "desktop",
            "expected_widget": "clock",
        },
    ]

    for i, case in enumerate(test_cases, 1):
        result = module(
            designed_data={
                "query": case["query"],
                "data_type": case["data_type"],
            },
            device_context=case["device_context"],
        )

        widgets = result.get("widgets", [])
        rationale = result.get("rationale", "")

        print(f"\n  Test {i}: {case['query'][:50]}...")
        print(f"    Data type: {case['data_type']}")
        print(f"    Selected widgets: {widgets}")
        print(f"    Rationale: {rationale[:80]}...")

        # Verify
        assert isinstance(widgets, list), "Widgets should be a list"
        assert len(widgets) > 0, "Should select at least one widget"
        assert all(w in module.VALID_WIDGETS for w in widgets), f"Invalid widget in {widgets}"

        # Check if expected widget is in the selection
        if case["expected_widget"] in widgets:
            print(f"    ✓ Expected '{case['expected_widget']}' was selected")


def test_widget_matcher_complex():
    """Test widget matching with complex, ambiguous queries."""
    print("\n=== Test: Widget Matcher - Complex Queries ===")

    module = WidgetMatcherModule()

    complex_cases = [
        {
            "query": "I need to visualize sales data broken down by region and quarter, "
                     "showing trends over the past 5 years with comparisons between products",
            "data_type": "numerical_time_series",
        },
        {
            "query": "Create a dashboard showing project status, team assignments, "
                     "deadlines, and progress percentages for all active sprints",
            "data_type": "general",
        },
        {
            "query": "Display customer reviews with ratings, photos, and timestamps "
                     "in a scrollable format with filtering options",
            "data_type": "visual_image",
        },
        {
            "query": "Build an interactive calculator for mortgage payments with "
                     "amortization schedule and pie chart breakdown",
            "data_type": "numerical_time_series",
        },
    ]

    for i, case in enumerate(complex_cases, 1):
        result = module(
            designed_data={
                "query": case["query"],
                "data_type": case["data_type"],
            },
            device_context="desktop",
        )

        widgets = result.get("widgets", [])
        rationale = result.get("rationale", "")

        print(f"\n  Complex Query {i}:")
        print(f"    Query: {case['query'][:80]}...")
        print(f"    Selected: {widgets}")
        print(f"    Reasoning: {rationale[:100]}...")

        # Verify all widgets are valid
        for w in widgets:
            assert w in module.VALID_WIDGETS, f"Invalid widget: {w}"


def test_widget_matcher_device_context():
    """Test widget matching with different device contexts."""
    print("\n=== Test: Widget Matcher - Device Context ===")

    module = WidgetMatcherModule()

    query = "Show me the weather forecast for this week"
    data_type = "numerical_time_series"

    devices = ["mobile", "desktop", "tablet"]

    for device in devices:
        result = module(
            designed_data={"query": query, "data_type": data_type},
            device_context=device,
        )

        widgets = result.get("widgets", [])

        print(f"\n  Device: {device}")
        print(f"    Selected widgets: {widgets}")
        print(f"    Rationale: {result.get('rationale', '')[:60]}...")


def test_widget_matcher_edge_cases():
    """Test widget matching with edge cases."""
    print("\n=== Test: Widget Matcher - Edge Cases ===")

    module = WidgetMatcherModule()

    # Edge case 1: Empty query
    result = module(
        designed_data={"query": "", "data_type": "general"},
        device_context="desktop",
    )
    print(f"\n  Empty query: {result.get('widgets', [])}")
    assert result.get("widgets"), "Should handle empty query gracefully"

    # Edge case 2: Unknown data type
    result = module(
        designed_data={"query": "Something random", "data_type": "unknown_type"},
        device_context="desktop",
    )
    print(f"  Unknown data type: {result.get('widgets', [])}")
    assert result.get("widgets"), "Should handle unknown data type"

    # Edge case 3: Very long query
    long_query = "AI " * 100 + "machine learning"
    result = module(
        designed_data={"query": long_query, "data_type": "general"},
        device_context="desktop",
    )
    print(f"  Very long query: {result.get('widgets', [])}")


def test_widget_selector_agent_basic():
    """Test WidgetSelectorAgent with basic queries."""
    print("\n=== Test: Widget Selector Agent - Basic ===")

    agent = WidgetSelectorAgent()

    test_cases = [
        {
            "query": "Show stock prices",
            "data_type": "numerical_time_series",
            "metadata": {"url_count": 0},
        },
        {
            "query": "Find information about Python",
            "data_type": "general",
            "metadata": {"url_count": 5},  # Multiple URLs
        },
        {
            "query": "What is machine learning?",
            "data_type": "general",
            "metadata": {"url_count": 1},  # Single URL
        },
    ]

    for i, case in enumerate(test_cases, 1):
        designed_data = {
            "query": case["query"],
            "data_type": case["data_type"],
            "metadata": case["metadata"],
        }

        result = agent(designed_data=designed_data, device_context="desktop")

        print(f"\n  Case {i}: {case['query']}")
        print(f"    URL count: {case['metadata']['url_count']}")
        print(f"    Selected widgets: {result.get('widgets', [])}")
        print(f"    Rationale: {result.get('rationale', '')[:80]}...")

        # Verify structure
        assert isinstance(result, dict), "Result should be a dict"
        assert "widgets" in result, "Missing widgets key"
        assert "rationale" in result, "Missing rationale key"


def test_widget_selector_agent_url_scenarios():
    """Test WidgetSelectorAgent URL-specific scenarios."""
    print("\n=== Test: Widget Selector Agent - URL Scenarios ===")

    agent = WidgetSelectorAgent()

    # Scenario 1: URL-related query with multiple results
    multi_url_data = {
        "query": "search for tutorials about React and Vue frameworks",
        "data_type": "general",
        "metadata": {"url_count": 8},
    }

    result = agent(designed_data=multi_url_data, device_context="desktop")

    print("\n  Multiple URLs scenario:")
    print(f"    Query: {multi_url_data['query']}")
    print(f"    URL count: {multi_url_data['metadata']['url_count']}")
    print(f"    Selected: {result.get('widgets', [])}")
    print("    Expected: ['gallery', 'markdown'] or similar")

    # Scenario 2: URL-related query with single result
    single_url_data = {
        "query": "find information about quantum computing",
        "data_type": "general",
        "metadata": {"url_count": 1},
    }

    result = agent(designed_data=single_url_data, device_context="desktop")

    print("\n  Single URL scenario:")
    print(f"    Query: {single_url_data['query']}")
    print(f"    URL count: {single_url_data['metadata']['url_count']}")
    print(f"    Selected: {result.get('widgets', [])}")
    print("    Expected: ['image', 'markdown'] or similar")

    # Scenario 3: Non-URL query
    non_url_data = {
        "query": "explain how neural networks work",
        "data_type": "general",
        "metadata": {"url_count": 0},
    }

    result = agent(designed_data=non_url_data, device_context="desktop")

    print("\n  Non-URL scenario:")
    print(f"    Query: {non_url_data['query']}")
    print(f"    URL count: {non_url_data['metadata']['url_count']}")
    print(f"    Selected: {result.get('widgets', [])}")
    print(f"    Rationale: {result.get('rationale', '')[:80]}...")


def test_widget_selector_agent_fallback():
    """Test WidgetSelectorAgent fallback mechanism."""
    print("\n=== Test: Widget Selector Agent - Fallback ===")

    agent = WidgetSelectorAgent()

    # Test fallback widget suggestion
    fallback_data = agent.suggest_fallback_widget(error_type="data_processing_error")
    print(f"\n  Data error fallback: {fallback_data}")
    assert fallback_data, "Should suggest fallback widget"

    fallback_visual = agent.suggest_fallback_widget(error_type="visual_render_error")
    print(f"  Visual error fallback: {fallback_visual}")
    assert fallback_visual, "Should suggest fallback widget"

    fallback_default = agent.suggest_fallback_widget(error_type="unknown_error")
    print(f"  Unknown error fallback: {fallback_default}")
    assert fallback_default == "markdown", "Default fallback should be markdown"


def test_widget_selector_real_world():
    """Test WidgetSelectorAgent with real-world scenarios."""
    print("\n=== Test: Widget Selector Agent - Real-World Scenarios ===")

    agent = WidgetSelectorAgent()

    scenarios = [
        {
            "name": "E-commerce Dashboard",
            "query": "Show sales analytics with revenue trends, top products, and customer demographics",
            "data_type": "numerical_time_series",
            "metadata": {"url_count": 0},
        },
        {
            "name": "Recipe Search",
            "query": "search for pasta recipes with images and cooking instructions",
            "data_type": "visual_image",
            "metadata": {"url_count": 12},
        },
        {
            "name": "Stock Portfolio",
            "query": "Display my stock portfolio with current prices and daily changes",
            "data_type": "numerical_time_series",
            "metadata": {"url_count": 0},
        },
        {
            "name": "Article Lookup",
            "query": "find information about climate change effects on marine life",
            "data_type": "general",
            "metadata": {"url_count": 1},
        },
    ]

    for scenario in scenarios:
        print(f"\n  {scenario['name']}:")
        print(f"    Query: {scenario['query'][:60]}...")

        result = agent(
            designed_data={
                "query": scenario["query"],
                "data_type": scenario["data_type"],
                "metadata": scenario["metadata"],
            },
            device_context="desktop",
        )

        print(f"    Widgets: {result.get('widgets', [])}")
        print(f"    Rationale: {result.get('rationale', '')[:100]}...")


def run_all_selector_tests():
    """Run all selector and pipeline tests."""
    print("=" * 60)
    print("SELECTOR TOOLS & PIPELINE TEST SUITE")
    print("=" * 60)
    print("Using model: ollama_chat/qwen3:8b")

    tests = [
        test_widget_matcher_basic,
        test_widget_matcher_complex,
        test_widget_matcher_device_context,
        test_widget_matcher_edge_cases,
        test_widget_selector_agent_basic,
        test_widget_selector_agent_url_scenarios,
        test_widget_selector_agent_fallback,
        test_widget_selector_real_world,
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
    success = run_all_selector_tests()
    sys.exit(0 if success else 1)

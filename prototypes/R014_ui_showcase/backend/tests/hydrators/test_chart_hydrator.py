#!/usr/bin/env python3
"""Unit test for ChartHydratorModule with ollama/qwen3:8b."""

import dspy
from services.tools.hydrators.chart_hydrator import ChartHydratorModule


def test_chart_hydrator_with_qwen():
    """Test ChartHydratorModule in isolation with ollama/qwen3:8b."""

    # Configure DSPy with Ollama
    lm = dspy.LM("ollama_chat/qwen3:8b", api_base="http://localhost:11434")
    dspy.configure(lm=lm)

    # Mock extracted_numbers data (similar to what logs showed)
    mock_extracted_numbers = [
        {
            "label": "India",
            "value": "7.74",
            "unit": "%",
            "context": "inflation rate 2024",
            "year": "2024",
        },
        {
            "label": "United States",
            "value": "3.7",
            "unit": "%",
            "context": "inflation rate 2024",
            "year": "2024",
        },
        {
            "label": "Brazil",
            "value": "5.8",
            "unit": "%",
            "context": "inflation rate 2024",
            "year": "2024",
        },
        {
            "label": "Eurozone",
            "value": "5.2",
            "unit": "%",
            "context": "inflation rate 2024",
            "year": "2024",
        },
        {
            "label": "China",
            "value": "1.9",
            "unit": "%",
            "context": "inflation rate 2024",
            "year": "2024",
        },
        {
            "label": "World",
            "value": "2.95",
            "unit": "%",
            "context": "inflation rate 2024",
            "year": "2024",
        },
    ]

    # Create presentation_ready input
    presentation_ready = {
        "query": "Explain in detail with internet search data as citations and charts and graphs, and a report about global inflation trends",
        "researched_data": {
            "extracted_numbers": mock_extracted_numbers,
        },
        "design": {
            "domain": "economics",
        },
    }

    # Initialize and run the chart hydrator
    print("=" * 80)
    print("Testing ChartHydratorModule with ollama/qwen3:8b")
    print("=" * 80)

    hydrator = ChartHydratorModule()

    print("\n📊 Calling ChartHydratorModule...")
    print(f"   Input: {len(mock_extracted_numbers)} extracted numbers")
    print()

    result = hydrator(presentation_ready=presentation_ready)

    print("\n📦 Result:")
    content = result.get("content", {})
    print(f"   Type: {content.get('type')}")
    print(f"   Title: {content.get('title')}")
    print(f"   X-axis: {content.get('x_axis')}")
    print(f"   Y-axis: {content.get('y_axis')}")
    print(f"   Data points: {len(content.get('data', []))}")
    print()

    print("📊 Chart Data:")
    chart_data = content.get("data", [])
    for i, point in enumerate(chart_data[:10]):
        print(f"   {i + 1}. {point}")

    if len(chart_data) > 10:
        print(f"   ... and {len(chart_data) - 10} more points")

    # Assertions
    assert content.get("type") in ["bar", "line", "area", "pie", "radar", "radial"], (
        f"Invalid chart type: {content.get('type')}"
    )
    assert len(chart_data) > 0, "Chart data is empty!"
    assert content.get("title"), "Chart title is missing!"

    print("\n" + "=" * 80)
    print("✅ All assertions passed!")
    print("=" * 80)


if __name__ == "__main__":
    test_chart_hydrator_with_qwen()

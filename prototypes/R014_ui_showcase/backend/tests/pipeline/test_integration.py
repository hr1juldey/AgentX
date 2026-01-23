#!/usr/bin/env python3
"""
Integration tests for full pipeline workflows.
Tests end-to-end flows from user query to final output.
"""

import sys
from pathlib import Path

# Add backend to path (2 levels up from tests/)
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Configure DSPy with Ollama BEFORE importing modules
import dspy

lm = dspy.LM(
    "ollama_chat/qwen3:8b",
    api_base="http://localhost:11434",
    api_key="",
)
dspy.configure(lm=lm)

from services.pipeline.analyst import AnalystAgent
from services.pipeline.data_contextualizer import DataContextualizerAgent
from services.pipeline.researcher import ResearcherAgent
from services.pipeline.widget_selector import WidgetSelectorAgent


def test_full_research_workflow():
    """Test complete workflow: Analyst → Researcher → Output."""
    print("\n=== Integration Test: Full Research Workflow ===")

    analyst = AnalystAgent()
    researcher = ResearcherAgent()

    query = "What are the environmental impacts of electric vehicles?"

    print(f"  Query: '{query}'")

    # Step 1: Initial Analysis
    print("\n  Step 1: Analyst (Pass 1 - Initial Analysis)")
    analysis = analyst(
        user_query=query,
        device_context="desktop",
        pass_number=1,
    )

    print(f"    Domain: {analysis.get('domain', 'N/A')}")
    print(f"    Goal: {analysis.get('goal', 'N/A')[:60]}...")
    print(f"    Search terms: {analysis.get('search_terms', [])[:3]}")
    print(f"    Insights: {len(analysis.get('insights', []))}")

    # Verify Step 1
    assert "query_type" in analysis
    assert "domain" in analysis
    assert "search_terms" in analysis
    assert len(analysis.get("search_terms", [])) > 0

    # Step 2: Research
    print("\n  Step 2: Researcher")
    try:
        research_result = researcher(analysis=analysis)

        print(f"    Raw data: {len(research_result.get('raw_data', []))} items")
        print(f"    Key facts: {len(research_result.get('structured_data', {}).get('key_facts', []))}")
        print(f"    Trends: {len(research_result.get('structured_data', {}).get('trends', []))}")
        print(f"    Citations: {len(research_result.get('citations', []))}")

        # Verify Step 2
        assert "raw_data" in research_result
        assert "beautiful_data" in research_result
        assert "structured_data" in research_result
        assert "citations" in research_result

    except Exception as e:
        print(f"    ⚠ Research failed (may be offline): {e}")
        research_result = None

    print("\n  ✓ Workflow completed!")

    return {
        "analysis": analysis,
        "research": research_result,
    }


def test_widget_selection_workflow():
    """Test workflow: Analyst → Researcher → WidgetSelector."""
    print("\n=== Integration Test: Widget Selection Workflow ===")

    analyst = AnalystAgent()
    researcher = ResearcherAgent()
    widget_selector = WidgetSelectorAgent()

    query = "Show me stock prices for tech companies over time"

    print(f"  Query: '{query}'")

    # Step 1: Analysis
    print("\n  Step 1: Analyst")
    analysis = analyst(
        user_query=query,
        device_context="desktop",
        pass_number=1,
    )

    print(f"    Domain: {analysis.get('domain', 'N/A')}")

    # Step 2: Research (mock if offline)
    print("\n  Step 2: Researcher")
    try:
        research_result = researcher(analysis=analysis)
        print(f"    Data type: {research_result.get('data_type', 'N/A')}")
    except Exception as e:
        print(f"    ⚠ Using mock research: {e}")
        research_result = {
            "data_type": "numerical_time_series",
            "structured_data": {"key_facts": ["Mock data"]},
        }

    # Step 3: Widget Selection
    print("\n  Step 3: WidgetSelector")
    designed_data = {
        "query": query,
        "data_type": research_result.get("data_type", "general"),
        "metadata": {"url_count": len(research_result.get("raw_data", []))},
    }

    widget_result = widget_selector(
        designed_data=designed_data,
        device_context="desktop",
    )

    print(f"    Selected widgets: {widget_result.get('widgets', [])}")
    print(f"    Rationale: {widget_result.get('rationale', '')[:80]}...")

    # Verify widget selection makes sense
    widgets = widget_result.get("widgets", [])
    assert len(widgets) > 0, "Should select at least one widget"

    # For stock prices over time, chart is a good choice
    if "chart" in widgets:
        print("    ✓ Correctly selected 'chart' for time-series stock data")

    print("\n  ✓ Widget selection workflow completed!")

    return {
        "widgets": widgets,
        "rationale": widget_result.get("rationale", ""),
    }


def test_contextualization_workflow():
    """Test workflow with data contextualization."""
    print("\n=== Integration Test: Contextualization Workflow ===")

    analyst = AnalystAgent()
    contextualizer = DataContextualizerAgent()

    query = "What are the latest trends in renewable energy?"

    print(f"  Query: '{query}'")

    # Step 1: Initial Analysis
    print("\n  Step 1: Analyst (Pass 1)")
    analysis = analyst(
        user_query=query,
        device_context="desktop",
        pass_number=1,
    )

    print(f"    Search terms: {analysis.get('search_terms', [])[:3]}")

    # Step 2: Mock research data (format expected by DataContextualizerAgent)
    print("\n  Step 2: Mock Research Data")
    mock_research_data = {
        "query": query,
        "raw_data": [
            {
                "title": "Solar Energy Growth 2025",
                "snippet": "Solar installations increased by 30%...",
                "url": "https://example.com/solar",
                "content": "Solar energy capacity grew by 30% in 2025..."
            },
            {
                "title": "Wind Power Trends",
                "snippet": "Wind energy now accounts for 10%...",
                "url": "https://example.com/wind",
                "content": "Wind power provides 10% of global electricity..."
            },
            {
                "title": "Battery Technology Advances",
                "snippet": "New battery designs improve storage...",
                "url": "https://example.com/battery",
                "content": "New battery technologies enable longer storage..."
            },
        ],
        "beautiful_data": {
            "key_facts": ["Solar grew 30%", "Wind at 10%", "Battery tech improved"],
            "trends": ["Renewable adoption increasing", "Storage costs dropping"],
            "comparisons": [],
        }
    }

    print(f"    Mock data: {len(mock_research_data['raw_data'])} items")

    # Step 3: Contextualization (using correct API)
    print("\n  Step 3: Contextualizer")
    try:
        contextualized = contextualizer(
            research_data=mock_research_data,
            original_query=query,
        )

        print(f"    Contextualized data: {len(contextualized.get('contextualized_data', []))}")
        print(f"    Query relevance: {contextualized.get('query_relevance', 'N/A')}")

    except Exception as e:
        print(f"    ⚠ Contextualization failed: {e}")
        import traceback
        traceback.print_exc()
        contextualized = mock_research_data

    # Step 4: Data Judgment
    print("\n  Step 4: Analyst (Pass 2 - Judgment)")
    judgment = analyst(
        user_query=query,
        contextualized_data=contextualized,
        pass_number=2,
    )

    print(f"    Quality score: {judgment.get('quality_score', 'N/A')}")
    print(f"    Completeness: {judgment.get('completeness', 'N/A')}")

    print("\n  ✓ Contextualization workflow completed!")

    return {
        "contextualized": contextualized,
        "judgment": judgment,
    }


def test_multi_domain_queries():
    """Test workflow across different domains."""
    print("\n=== Integration Test: Multi-Domain Queries ===")

    analyst = AnalystAgent()

    domains = [
        ("What is quantum entanglement?", "physics"),
        ("Explain the Fed's interest rate policy", "economics"),
        ("How does CRISPR gene editing work?", "biology"),
        ("Compare Python vs JavaScript", "programming"),
    ]

    for query, expected_domain in domains:
        print(f"\n  Query: '{query[:50]}...'")
        print(f"    Expected domain: {expected_domain}")

        result = analyst(
            user_query=query,
            device_context="desktop",
            pass_number=1,
        )

        detected_domain = result.get("domain", "unknown")
        print(f"    Detected domain: {detected_domain}")

        # Check if domain is close to expected
        if expected_domain.lower() in detected_domain.lower():
            print("    ✓ Domain match!")


def test_error_recovery_workflow():
    """Test workflow behavior with errors/edge cases."""
    print("\n=== Integration Test: Error Recovery ===")

    analyst = AnalystAgent()

    edge_cases = [
        "",  # Empty query
        "xyz",  # Very short, ambiguous
        "a" * 500,  # Very long query without clear meaning
    ]

    for query in edge_cases:
        print(f"\n  Query: '{query[:50]}...'")

        try:
            result = analyst(
                user_query=query,
                device_context="desktop",
                pass_number=1,
            )

            print(f"    Query type: {result.get('query_type', 'N/A')}")
            print("    Handled gracefully: ✓")

        except Exception as e:
            print(f"    Error: {e}")


def test_end_to_end_real_world():
    """Test complete end-to-end real-world scenario."""
    print("\n=== Integration Test: End-to-End Real-World ===")

    analyst = AnalystAgent()
    researcher = ResearcherAgent()
    widget_selector = WidgetSelectorAgent()

    # Real-world scenario: User wants to understand a complex topic
    query = "What are the pros and cons of remote work in 2025?"

    print(f"  User Query: '{query}'")
    print("  Device: desktop")

    # Full pipeline
    print("\n" + "=" * 50)
    print("  PIPELINE EXECUTION")
    print("=" * 50)

    # Phase 1: Analysis
    print("\n  Phase 1: ANALYST (Initial Analysis)")
    analysis = analyst(
        user_query=query,
        device_context="desktop",
        pass_number=1,
    )

    print(f"    Query type: {analysis.get('query_type')}")
    print(f"    Domain: {analysis.get('domain')}")
    print(f"    Goal: {analysis.get('goal')[:80]}...")
    print(f"    Search terms: {', '.join(analysis.get('search_terms', [])[:3])}")
    print(f"    Insights extracted: {len(analysis.get('insights', []))}")

    # Phase 2: Research
    print("\n  Phase 2: RESEARCHER (Data Gathering)")
    try:
        research_result = researcher(analysis=analysis)

        raw_count = len(research_result.get('raw_data', []))
        facts_count = len(research_result.get('structured_data', {}).get('key_facts', []))
        trends_count = len(research_result.get('structured_data', {}).get('trends', []))
        citations_count = len(research_result.get('citations', []))

        print(f"    Sources found: {raw_count}")
        print(f"    Key facts: {facts_count}")
        print(f"    Trends: {trends_count}")
        print(f"    Citations: {citations_count}")
        print(f"    Data type: {research_result.get('data_type')}")

        research_success = True
    except Exception as e:
        print(f"    ⚠ Research offline: {e}")
        print("    Using mock data for widget selection...")
        research_result = {"data_type": "general", "raw_data": []}
        research_success = False

    # Phase 3: Widget Selection
    print("\n  Phase 3: WIDGET SELECTOR")
    designed_data = {
        "query": query,
        "data_type": research_result.get("data_type", "general"),
        "metadata": {"url_count": len(research_result.get("raw_data", []))},
    }

    widget_result = widget_selector(
        designed_data=designed_data,
        device_context="desktop",
    )

    widgets = widget_result.get('widgets', [])
    rationale = widget_result.get('rationale', '')

    print(f"    Recommended widgets: {widgets}")
    print(f"    Rationale: {rationale[:100]}...")

    # Final Summary
    print("\n" + "=" * 50)
    print("  PIPELINE SUMMARY")
    print("=" * 50)
    print(f"  Query: {query}")
    print(f"  Domain: {analysis.get('domain')}")
    print(f"  Insights: {len(analysis.get('insights', []))}")
    if research_success:
        print(f"  Sources: {raw_count}")
        print(f"  Facts: {facts_count}")
    print(f"  Widgets: {widgets}")
    print("\n  ✓ End-to-end workflow completed!")


def run_all_integration_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("INTEGRATION TEST SUITE")
    print("=" * 60)
    print("Using model: ollama_chat/qwen3:8b")

    tests = [
        test_full_research_workflow,
        test_widget_selection_workflow,
        test_contextualization_workflow,
        test_multi_domain_queries,
        test_error_recovery_workflow,
        test_end_to_end_real_world,
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
    success = run_all_integration_tests()
    sys.exit(0 if success else 1)

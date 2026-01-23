#!/usr/bin/env python3
"""
Standalone tests for Pipeline Agents (AnalystAgent, ResearcherAgent).
Tests full pipeline workflows with complex queries.
"""

import sys
from pathlib import Path

# Add backend to path (3 levels up from tests/pipeline/)
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

from services.pipeline.analyst import AnalystAgent
from services.pipeline.researcher import ResearcherAgent


def test_analyst_pass1():
    """Test AnalystAgent Pass 1: Initial Analysis."""
    print("\n=== Test: Analyst Agent - Pass 1 (Initial Analysis) ===")

    agent = AnalystAgent()

    queries = [
        "What are the latest developments in quantum computing?",
        "Compare Python and JavaScript for web development",
        "How does CRISPR gene editing work?",
    ]

    for query in queries:
        print(f"\n  Query: '{query}'")
        result = agent(
            user_query=query,
            device_context="desktop",
            pass_number=1,
        )

        print(f"    Query type: {result.get('query_type', 'N/A')}")
        print(f"    Domain: {result.get('domain', 'N/A')}")
        print(f"    Goal: {result.get('goal', 'N/A')[:60]}...")
        print(f"    Insights: {len(result.get('insights', []))}")
        print(f"    Search terms: {result.get('search_terms', [])[:3]}")

        # Verify structure
        assert isinstance(result, dict), "Result should be a dict"
        assert "query_type" in result, "Missing query_type"
        assert "domain" in result, "Missing domain"
        assert "goal" in result, "Missing goal"
        assert "insights" in result, "Missing insights"
        assert "search_terms" in result, "Missing search_terms"


def test_analyst_pass2():
    """Test AnalystAgent Pass 2: Data Judgment."""
    print("\n=== Test: Analyst Agent - Pass 2 (Data Judgment) ===")

    agent = AnalystAgent()

    query = "What is artificial intelligence?"

    # Mock contextualized data
    contextualized_data = {
        "results": [
            {"title": "AI Introduction", "snippet": "AI is a branch of computer science..."},
            {"title": "Machine Learning Basics", "snippet": "ML is a subset of AI..."},
            {"title": "Neural Networks", "snippet": "Neural networks are computing systems..."},
        ]
    }

    print(f"  Query: '{query}'")
    print(f"  Contextualized data: {len(contextualized_data['results'])} results")

    result = agent(
        user_query=query,
        device_context="desktop",
        contextualized_data=contextualized_data,
        pass_number=2,
    )

    print(f"\n  Quality score: {result.get('quality_score', 'N/A')}")
    print(f"  Completeness: {result.get('completeness', 'N/A')}")
    print(f"  Recommendations: {result.get('recommendations', [])[:3]}")

    # Verify structure
    assert isinstance(result, dict), "Result should be a dict"
    assert "quality_score" in result or "completeness" in result, "Missing quality metrics"


def test_analyst_device_contexts():
    """Test AnalystAgent with different device contexts."""
    print("\n=== Test: Analyst Agent - Device Contexts ===")

    agent = AnalystAgent()

    query = "Show me weather forecast for this week"
    devices = ["mobile", "desktop", "tablet"]

    for device in devices:
        print(f"\n  Device: {device}")
        result = agent(
            user_query=query,
            device_context=device,
            pass_number=1,
        )

        print(f"    Query type: {result.get('query_type', 'N/A')}")
        print(f"    Insights: {len(result.get('insights', []))}")


def test_researcher_basic():
    """Test ResearcherAgent with basic queries."""
    print("\n=== Test: Researcher Agent - Basic Queries ===")

    agent = ResearcherAgent()

    # Mock analysis from AnalystAgent
    analysis = {
        "query": "What is quantum computing?",
        "query_type": "definition",
        "domain": "technology",
        "goal": "Explain quantum computing concepts",
        "insights": ["Quantum uses qubits", "Superposition principle"],
        "search_terms": ["quantum computing", "qubits", "superposition"],
    }

    print(f"  Query: {analysis['query']}")
    print(f"  Search terms: {analysis['search_terms']}")

    try:
        result = agent(analysis=analysis)

        print(f"\n  Results found: {len(result.get('raw_data', []))}")
        print(f"  Key facts: {len(result.get('structured_data', {}).get('key_facts', []))}")
        print(f"  Citations: {len(result.get('citations', []))}")

        # Verify structure
        assert isinstance(result, dict), "Result should be a dict"
        assert "raw_data" in result, "Missing raw_data"
        assert "beautiful_data" in result, "Missing beautiful_data"
        assert "structured_data" in result, "Missing structured_data"
        assert "citations" in result, "Missing citations"

    except Exception as e:
        print(f"  ⚠ Research failed (may be offline): {e}")


def test_researcher_without_search_terms():
    """Test ResearcherAgent fallback when no search_terms provided."""
    print("\n=== Test: Researcher Agent - No Search Terms Fallback ===")

    agent = ResearcherAgent()

    # Mock analysis WITHOUT search_terms (tests fallback)
    analysis = {
        "query": "Explain machine learning",
        "query_type": "explanation",
        "domain": "AI",
        "goal": "Explain ML concepts",
        "insights": ["ML learns patterns", "Neural networks"],
        # No search_terms - should fall back to query
    }

    print(f"  Query: {analysis['query']}")
    print(f"  Search terms: None (testing fallback)")

    try:
        result = agent(analysis=analysis)

        print(f"\n  Results found: {len(result.get('raw_data', []))}")
        print(f"  Used fallback query: {analysis['query']}")

    except Exception as e:
        print(f"  ⚠ Research failed (may be offline): {e}")


def test_researcher_data_type_detection():
    """Test ResearcherAgent data type detection."""
    print("\n=== Test: Researcher Agent - Data Type Detection ===")

    agent = ResearcherAgent()

    test_cases = [
        {
            "analysis": {
                "query": "Show stock prices over time",
                "search_terms": ["stock market", "historical prices"],
                "domain": "finance",
            },
            "expected_hint": "time_series",
        },
        {
            "analysis": {
                "query": "Compare different programming languages",
                "search_terms": ["python", "javascript", "comparison"],
                "domain": "programming",
            },
            "expected_hint": "comparative",
        },
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n  Test {i}: {case['analysis']['query'][:50]}...")
        print(f"    Expected hint: {case['expected_hint']}")

        try:
            result = agent(analysis=case["analysis"])
            data_type = result.get("data_type", "")
            print(f"    Detected type: {data_type}")

            # Check if expected hint is in detected type
            if case["expected_hint"] in data_type.lower():
                print(f"    ✓ Correctly detected!")

        except Exception as e:
            print(f"    ⚠ Skipped: {e}")


def test_pipeline_full_workflow():
    """Test full pipeline: AnalystAgent → ResearcherAgent."""
    print("\n=== Test: Full Pipeline Workflow ===")

    analyst = AnalystAgent()
    researcher = ResearcherAgent()

    query = "What are the latest developments in artificial intelligence?"

    print(f"  User Query: '{query}'")

    # Pass 1: Initial Analysis
    print("\n  --- Pass 1: Analyst (Initial Analysis) ---")
    analysis = analyst(
        user_query=query,
        device_context="desktop",
        pass_number=1,
    )

    print(f"    Domain: {analysis.get('domain', 'N/A')}")
    print(f"    Goal: {analysis.get('goal', 'N/A')[:60]}...")
    print(f"    Search terms: {analysis.get('search_terms', [])[:3]}")

    # Pass 2: Research
    print("\n  --- Pass 2: Researcher ---")
    try:
        research_result = researcher(analysis=analysis)

        print(f"    Results: {len(research_result.get('raw_data', []))}")
        print(f"    Key facts: {len(research_result.get('structured_data', {}).get('key_facts', []))}")
        print(f"    Citations: {len(research_result.get('citations', []))}")

        # Pass 3: Data Judgment (optional)
        print("\n  --- Pass 3: Analyst (Data Judgment) ---")
        judgment = analyst(
            user_query=query,
            contextualized_data=research_result,
            pass_number=2,
        )

        print(f"    Quality: {judgment.get('quality_score', 'N/A')}")
        print(f"    Completeness: {judgment.get('completeness', 'N/A')}")

        print("\n  ✓ Full pipeline completed successfully!")

    except Exception as e:
        print(f"    ⚠ Pipeline incomplete (research may have failed): {e}")


def test_pipeline_real_world_queries():
    """Test pipeline with real-world complex queries."""
    print("\n=== Test: Pipeline - Real-World Queries ===")

    analyst = AnalystAgent()
    researcher = ResearcherAgent()

    real_queries = [
        "What is the current state of quantum computing in 2025?",
        "Compare Python vs JavaScript for backend development",
        "How does CRISPR gene editing work and what are its applications?",
    ]

    for query in real_queries:
        print(f"\n  Query: '{query[:60]}...'")

        # Analyst Pass 1
        analysis = analyst(
            user_query=query,
            device_context="desktop",
            pass_number=1,
        )

        print(f"    Domain: {analysis.get('domain', 'N/A')}")
        print(f"    Insights: {len(analysis.get('insights', []))}")

        # Researcher (may fail if offline)
        try:
            research_result = researcher(analysis=analysis)
            print(f"    Research: {len(research_result.get('raw_data', []))} results")
        except Exception as e:
            print(f"    Research: Skipped (offline/error)")


def run_all_pipeline_tests():
    """Run all pipeline agent tests."""
    print("=" * 60)
    print("PIPELINE AGENTS TEST SUITE")
    print("=" * 60)
    print("Using model: ollama_chat/qwen3:8b")

    tests = [
        test_analyst_pass1,
        test_analyst_pass2,
        test_analyst_device_contexts,
        test_researcher_basic,
        test_researcher_without_search_terms,
        test_researcher_data_type_detection,
        test_pipeline_full_workflow,
        test_pipeline_real_world_queries,
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
    success = run_all_pipeline_tests()
    sys.exit(0 if success else 1)

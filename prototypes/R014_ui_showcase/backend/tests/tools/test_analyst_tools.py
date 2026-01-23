#!/usr/bin/env python3
"""
Standalone tests for Analyst tools.
Tests ContextAnalyzerModule and InsightExtractorModule with complex queries.
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

from services.tools.analyst.query_analyzer import (
    ContextAnalyzerModule,
    InsightExtractorModule,
)


def test_context_analyzer_simple():
    """Test context analysis with simple queries."""
    print("\n=== Test: Context Analyzer - Simple Queries ===")

    module = ContextAnalyzerModule()

    queries = [
        "What is artificial intelligence?",
        "Compare Python and JavaScript",
        "How do I fix a broken pipe?",
    ]

    for query in queries:
        result = module(query=query)
        print(f"\n  Query: '{query}'")
        print(f"    Type: {result.get('query_type', 'N/A')}")
        print(f"    Domain: {result.get('domain', 'N/A')}")
        print(f"    Urgency: {result.get('urgency', 'N/A')}")

        # Verify structure
        assert isinstance(result, dict), "Result should be a dict"
        assert "query_type" in result, "Missing query_type"


def test_context_analyzer_complex():
    """Test context analysis with complex, multi-part queries."""
    print("\n=== Test: Context Analyzer - Complex Queries ===")

    module = ContextAnalyzerModule()

    # Complex query with multiple aspects
    complex_query = """
    I need to understand the differences between supervised and unsupervised learning
    in machine learning, specifically focusing on neural networks and deep learning
    applications in computer vision. This is for a research paper due next week.
    """

    result = module(query=complex_query)

    print(f"\n  Complex Query Analysis:")
    print(f"    Type: {result.get('query_type', 'N/A')}")
    print(f"    Domain: {result.get('domain', 'N/A')}")
    print(f"    Urgency: {result.get('urgency', 'N/A')}")

    assert isinstance(result, dict), "Result should be a dict"


def test_insight_extractor_small():
    """Test insight extraction with small text (direct path)."""
    print("\n=== Test: Insight Extractor - Small Text (Direct Path) ===")

    module = InsightExtractorModule()

    # Small query (< 500 chars) - should use fast path
    small_query = "AI is transforming healthcare through diagnostic assistance and personalized medicine."

    result = module(query=small_query)

    print(f"\n  Query: '{small_query}'")
    print(f"    Insights count: {len(result.get('insights', []))}")
    print(f"    Insights:")
    for i, insight in enumerate(result.get('insights', []), 1):
        print(f"      {i}. {insight}")

    # Verify
    assert isinstance(result, dict), "Result should be a dict"
    assert "insights" in result, "Missing insights key"
    assert isinstance(result["insights"], list), "Insights should be a list"

    # Check insights are meaningful (not just 2-3 chars)
    for insight in result["insights"]:
        assert len(insight) >= 10, f"Insight too short: '{insight}'"

    print("\n  ✓ Direct path working, insights are meaningful (not corrupted)")


def test_insight_extractor_large():
    """Test insight extraction with large text (chunked path)."""
    print("\n=== Test: Insight Extractor - Large Text (Chunked Path) ===")

    module = InsightExtractorModule()

    # Large query (> 500 chars) - should trigger chunking
    large_query = """
    Artificial intelligence has revolutionized numerous fields in recent years.
    Machine learning algorithms can now recognize patterns in vast datasets that
    would be impossible for humans to discern. Deep learning, a subset of ML,
    uses neural networks with multiple layers to learn hierarchical representations
    of data. This has led to breakthroughs in computer vision, natural language
    processing, and speech recognition. However, challenges remain including
    interpretability, bias, and the need for massive computational resources.
    Transformers have emerged as a powerful architecture, enabling models like
    GPT to generate human-like text. The future of AI lies in developing more
    efficient, interpretable, and fair systems that can reason about the world.
    """ * 2  # Make it even larger

    print(f"  Query length: {len(large_query)} characters")

    result = module(query=large_query)

    print(f"\n  Insights count: {len(result.get('insights', []))}")
    print(f"  Insights:")
    for i, insight in enumerate(result.get('insights', [])[:10], 1):
        print(f"    {i}. {insight[:80]}...")

    # Verify no corruption (each insight should be meaningful)
    assert isinstance(result, dict), "Result should be a dict"
    assert "insights" in result, "Missing insights key"

    insights = result.get("insights", [])
    for i, insight in enumerate(insights):
        if len(insight) < 10:
            print(f"  ✗ WARNING: Insight {i} appears corrupted: '{insight}'")
            raise AssertionError(f"Insight {i} is too short: '{insight}'")

    print(f"\n  ✓ Chunked path working, all {len(insights)} insights are meaningful")


def test_insight_extractor_edge_cases():
    """Test insight extraction with edge cases."""
    print("\n=== Test: Insight Extractor - Edge Cases ===")

    module = InsightExtractorModule()

    # Edge case 1: Very short query
    very_short = "AI"
    result = module(query=very_short)
    print(f"\n  Very short query ('{very_short}'): {len(result.get('insights', []))} insights")

    # Edge case 2: Query with special characters
    special = "AI & ML: Deep learning, NLP, Computer Vision (CV) + Robotics!"
    result = module(query=special)
    print(f"  Special characters: {len(result.get('insights', []))} insights")

    # Edge case 3: Query with numbers
    numbers = "In 2023, AI market reached $500B. By 2030, it's projected to hit $3T."
    result = module(query=numbers)
    print(f"  Numbers and stats: {len(result.get('insights', []))} insights")


def test_insight_extractor_real_world():
    """Test insight extraction with real-world complex queries."""
    print("\n=== Test: Insight Extractor - Real-World Queries ===")

    module = InsightExtractorModule()

    real_queries = [
        # Technical documentation
        """
        Docker containers provide lightweight virtualization by sharing the host OS kernel.
        Each container runs in isolation with its own filesystem, networking, and process space.
        Images are built using Dockerfiles which specify base images, dependencies, and commands.
        Docker Compose orchestrates multi-container applications with services, networks, and volumes.
        """,

        # Business case study
        """
        Netflix's recommendation system processes 1 billion playback events per day.
        The system uses collaborative filtering to find similar users and content.
        Personalization increases viewer engagement by 20% and saves $1B annually
        in customer retention. The algorithm runs on Spark clusters with 1000+ nodes.
        """,

        # Scientific explanation
        """
        CRISPR-Cas9 is a revolutionary gene-editing tool derived from bacterial immune systems.
        The Cas9 protein is guided by RNA to specific DNA sequences where it creates double-strand breaks.
    This allows precise gene knockout, knock-in, and base editing. Applications include treating
        genetic diseases, developing drought-resistant crops, and creating disease models.
        """,
    ]

    titles = ["Docker Technology", "Netflix Recommendations", "CRISPR Gene Editing"]

    for query, title in zip(real_queries, titles):
        print(f"\n  {title}:")
        result = module(query=query.strip())
        insights = result.get("insights", [])
        print(f"    Length: {len(query.strip())} chars -> {len(insights)} insights")

        # Show first few insights
        for i, insight in enumerate(insights[:3], 1):
            print(f"      {i}. {insight[:70]}...")

        # Verify quality
        assert len(insights) > 0, f"{title}: Should return at least 1 insight"
        for insight in insights:
            assert len(insight) >= 10, f"{title}: Insight too short: '{insight}'"


def run_all_analyst_tests():
    """Run all analyst tool tests."""
    print("=" * 60)
    print("ANALYST TOOLS TEST SUITE")
    print("=" * 60)
    print("Using model: ollama_chat/qwen3:8b")

    tests = [
        test_context_analyzer_simple,
        test_context_analyzer_complex,
        test_insight_extractor_small,
        test_insight_extractor_large,
        test_insight_extractor_edge_cases,
        test_insight_extractor_real_world,
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
    success = run_all_analyst_tests()
    sys.exit(0 if success else 1)

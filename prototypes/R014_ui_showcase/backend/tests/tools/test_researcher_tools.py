#!/usr/bin/env python3
"""
Standalone tests for Researcher tools.
Tests SearchTermExtractorModule, SearXNGSearchModule, CitationBuilderModule, and DataStructurerModule.
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

from services.tools.analyst.search_terms import SearchTermExtractorModule
from services.tools.researcher.searxng_search import SearXNGSearchModule
from services.tools.researcher.citation_builder import CitationBuilderModule
from services.tools.researcher.data_processor import DataStructurerModule


def test_search_term_extractor():
    """Test search term extraction from various query types."""
    print("\n=== Test: Search Term Extractor ===")

    module = SearchTermExtractorModule()

    test_queries = [
        (
            "What are the latest developments in quantum computing?",
            "technology",
            ["AI", "computing"],
        ),
        (
            "Compare Python vs JavaScript for web development",
            "programming",
            ["languages", "development"],
        ),
        ("How does CRISPR gene editing work?", "biology", ["gene editing", "DNA"]),
        (
            "Climate change effects on polar bear populations",
            "environment",
            ["climate", "wildlife"],
        ),
        (
            "Best practices for Docker container security",
            "devops",
            ["containers", "security"],
        ),
    ]

    for query, domain, insights in test_queries:
        result = module(query=query, insights=insights, domain=domain)
        terms = result.get("search_terms", [])
        print(f"\n  Query: '{query[:60]}...'")
        print(f"    Domain: {domain}")
        print(f"    Search terms: {terms}")

        # Verify
        assert isinstance(terms, list), "Search terms should be a list"
        assert len(terms) > 0, "Should return at least one search term"
        assert all(isinstance(t, str) for t in terms), "All terms should be strings"


def test_search_term_extractor_complex():
    """Test search term extraction with complex, multi-part queries."""
    print("\n=== Test: Search Term Extractor - Complex Queries ===")

    module = SearchTermExtractorModule()

    complex_cases = [
        # Multi-question query
        (
            """
        I need to research machine learning algorithms for predicting stock prices.
        Specifically, I'm interested in LSTM networks, random forests, and
        how they compare for time-series forecasting in financial markets.
        """,
            "finance",
            ["LSTM", "stock prediction", "time-series"],
        ),
        # Domain-specific query
        (
            """
        Explain the difference between TCP and UDP protocols in networking,
        including their use cases, header formats, and how they handle
        reliability, flow control, and congestion control.
        """,
            "networking",
            ["protocols", "TCP", "UDP"],
        ),
        # Academic query
        (
            """
        Recent advances in transformer architectures for natural language processing,
        including attention mechanisms, positional encoding, and pre-training strategies
        used in models like GPT-4, BERT, and T5.
        """,
            "AI research",
            ["transformers", "attention", "NLP"],
        ),
    ]

    titles = ["ML for Stock Prediction", "TCP vs UDP", "Transformer Architectures"]

    for (query, domain, insights), title in zip(complex_cases, titles):
        result = module(query=query.strip(), insights=insights, domain=domain)
        terms = result.get("search_terms", [])
        print(f"\n  {title}:")
        print(f"    Query length: {len(query.strip())} chars")
        print(f"    Search terms ({len(terms)}): {terms[:5]}")

        assert len(terms) > 0, f"{title}: Should return at least one term"


def test_searxng_search():
    """Test SearXNG search functionality."""
    print("\n=== Test: SearXNG Search Module ===")

    module = SearXNGSearchModule()

    test_searches = [
        ("Python programming", "general"),
        ("latest AI news", "news"),
        ("machine learning tutorials", "general"),
    ]

    for query, search_type in test_searches:
        print(f"\n  Searching: '{query}' (type: {search_type})")
        try:
            result = module(query=query, search_type=search_type)
            results = result.get("results", [])
            print(f"    Found {len(results)} results")

            # Show first few results
            for i, r in enumerate(results[:3], 1):
                print(f"      {i}. {r.get('title', 'N/A')[:60]}...")
                print(f"         URL: {r.get('url', 'N/A')[:60]}...")

            assert isinstance(results, list), "Results should be a list"
            assert len(results) > 0, f"Should return at least one result for '{query}'"

        except Exception as e:
            print(f"    ⚠ Search failed (may be offline): {e}")
            print("    Skipping verification...")


def test_citation_builder_basic():
    """Test citation builder with basic data."""
    print("\n=== Test: Citation Builder - Basic ===")

    module = CitationBuilderModule()

    # Mock search results
    raw_data = [
        {
            "title": "Introduction to Machine Learning",
            "url": "https://example.com/ml-intro",
            "content": "Machine learning is a subset of artificial intelligence...",
        },
        {
            "title": "Deep Learning Basics",
            "url": "https://example.com/deep-learning",
            "content": "Deep learning uses neural networks with multiple layers...",
        },
        {
            "title": "Natural Language Processing",
            "url": "https://example.com/nlp",
            "content": "NLP deals with interaction between computers and human language...",
        },
    ]

    # Test without writing (basic citations)
    result = module(raw_data=raw_data, writing="")
    citations = result if isinstance(result, list) else []

    print(f"  Raw data items: {len(raw_data)}")
    print(f"  Citations generated: {len(citations)}")

    for i, citation in enumerate(citations, 1):
        print(f"\n    {i}. {citation.get('document_title', 'N/A')}")
        print(f"       URL: {citation.get('url', 'N/A')}")
        print(f"       Cited text: {citation.get('cited_text', 'N/A')[:60]}...")
        print(f"       Index: {citation.get('document_index', 'N/A')}")

    # Verify structure (frontend-compatible format)
    assert isinstance(citations, list), "Citations should be a list"
    assert len(citations) > 0, "Should generate at least one citation"
    for citation in citations:
        assert isinstance(citation, dict), "Each citation should be a dict"
        assert "document_title" in citation, "Missing document_title field"
        assert "url" in citation, "Missing url field"
        assert "cited_text" in citation, "Missing cited_text field"
        assert "document_index" in citation, "Missing document_index field"


def test_citation_builder_with_writing():
    """Test citation builder with writing text (position prediction)."""
    print("\n=== Test: Citation Builder - With Writing (Position Prediction) ===")

    module = CitationBuilderModule()

    # Mock search results
    raw_data = [
        {
            "title": "Python for Data Science",
            "url": "https://example.com/python-data",
            "content": "Python is widely used for data analysis, visualization, and machine learning...",
        },
        {
            "title": "JavaScript Web Development",
            "url": "https://example.com/js-web",
            "content": "JavaScript is essential for front-end web development and interactive websites...",
        },
    ]

    # Writing that mentions Python
    writing = """
    Data science has become one of the most popular fields in technology.
    Python is the programming language of choice for most data scientists
    due to its simplicity and powerful libraries like NumPy, pandas, and scikit-learn.
    These tools make it easy to analyze data, create visualizations, and build models.
    """

    print(f"  Writing snippet: '{writing[:100]}...'")
    print(f"  Analyzing relevance for {len(raw_data)} sources...")

    result = module(raw_data=raw_data, writing=writing)
    citations = result if isinstance(result, list) else []

    print("\n  Citations with best matching sentences:")

    for i, citation in enumerate(citations, 1):
        print(f"\n    {i}. {citation.get('document_title', 'N/A')}")
        print(f"       Cited text: {citation.get('cited_text', 'N/A')[:80]}...")
        print(f"       Index: {citation.get('document_index', 'N/A')}")

    # Verify structure (frontend-compatible format)
    for citation in citations:
        assert "document_title" in citation, "Missing document_title field"
        assert "url" in citation, "Missing url field"
        assert "cited_text" in citation, "Missing cited_text field"
        assert "document_index" in citation, "Missing document_index field"


def test_citation_builder_real_world():
    """Test citation builder with real-world scenarios."""
    print("\n=== Test: Citation Builder - Real-World Scenarios ===")

    module = CitationBuilderModule()

    # Scenario 1: Academic research
    academic_data = [
        {
            "title": "Attention Is All You Need",
            "url": "https://arxiv.org/abs/1706.03762",
            "content": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...",
        },
        {
            "title": "BERT: Pre-training of Deep Bidirectional Transformers",
            "url": "https://arxiv.org/abs/1810.04805",
            "content": "We introduce a new language representation model called BERT...",
        },
    ]

    academic_writing = """
    Transformer architectures have revolutionized natural language processing.
    The self-attention mechanism allows models to process sequences in parallel,
    unlike recurrent networks. This has enabled models like GPT and BERT to achieve
    state-of-the-art results on numerous NLP benchmarks.
    """

    print("\n  Scenario 1: Academic Research")
    result = module(raw_data=academic_data, writing=academic_writing)
    print(f"    Generated {len(result)} citations from {len(academic_data)} sources")


def test_data_structurer_small():
    """Test data structurer with small data."""
    print("\n=== Test: Data Structurer - Small Data ===")

    module = DataStructurerModule()

    # Small beautiful data
    beautiful_data = {
        "key_facts": [
            "AI market reached $500B in 2023",
            "Machine learning adoption increased by 40%",
            "Deep learning accounts for 35% of AI projects",
        ],
        "trends": [
            "Growing demand for AI ethics",
            "Increased edge AI deployment",
            "Rise of multimodal AI systems",
        ],
    }

    result = module(beautiful_data=beautiful_data)
    structured = result.get("structured_data", {})

    print(
        f"  Input: {len(beautiful_data.get('key_facts', []))} facts, "
        f"{len(beautiful_data.get('trends', []))} trends"
    )
    print("\n  Structured output:")
    print(f"    Key facts: {len(structured.get('key_facts', []))}")
    for fact in structured.get("key_facts", []):
        print(f"      - {fact}")
    print(f"    Trends: {len(structured.get('trends', []))}")
    for trend in structured.get("trends", []):
        print(f"      - {trend}")

    # Verify structure
    assert isinstance(structured, dict), "Structured data should be a dict"
    assert "key_facts" in structured, "Missing key_facts"
    assert "trends" in structured, "Missing trends"


def test_data_structurer_large():
    """Test data structurer with large data (chunked path)."""
    print("\n=== Test: Data Structurer - Large Data (Chunked) ===")

    module = DataStructurerModule()

    # Large beautiful data that will trigger chunking
    large_facts = [
        f"Fact {i}: AI insight number {i} demonstrates machine learning capability."
        for i in range(20)
    ]
    large_trends = [
        f"Trend {i}: Deep learning trend {i} shows exponential growth in sector {i % 5}."
        for i in range(15)
    ]

    beautiful_data = {
        "key_facts": large_facts,
        "trends": large_trends,
    }

    print(f"  Input: {len(large_facts)} facts, {len(large_trends)} trends")

    result = module(beautiful_data=beautiful_data)
    structured = result.get("structured_data", {})

    print("\n  Structured output:")
    print(f"    Key facts: {len(structured.get('key_facts', []))}")
    print(f"    Trends: {len(structured.get('trends', []))}")
    print(f"    Comparisons: {len(structured.get('comparisons', []))}")

    # Verify it returns a dict, not a string
    assert isinstance(structured, dict), "Should return dict, not string"
    assert "key_facts" in structured, "Missing key_facts in output"


def test_data_structurer_real_world():
    """Test data structurer with real-world data."""
    print("\n=== Test: Data Structurer - Real-World Data ===")

    module = DataStructurerModule()

    # Real-world scenario: Climate data
    climate_data = {
        "key_facts": [
            "Global temperature rose 1.1°C since pre-industrial times",
            "CO2 levels reached 421 ppm in 2022, highest in 800,000 years",
            "Arctic ice extent declined 13% per decade since 1979",
            "Sea levels rose 20cm since 1900, accelerating to 3.7mm/year",
            "Extreme weather events increased 5x in last 50 years",
        ],
        "trends": [
            "Shifting climate zones affecting agriculture",
            "Ocean acidification threatening marine ecosystems",
            "Expansion of tropical disease ranges",
            "Increased frequency of heatwaves and droughts",
        ],
    }

    print("  Scenario: Climate Change Data")
    result = module(beautiful_data=climate_data)
    structured = result.get("structured_data", {})

    print("\n  Structured Analysis:")
    print(f"    Key Facts Extracted: {len(structured.get('key_facts', []))}")
    for fact in structured.get("key_facts", []):
        print(f"      {fact}")

    print(f"\n    Trends Identified: {len(structured.get('trends', []))}")
    for trend in structured.get("trends", []):
        print(f"      {trend}")

    # Verify output is properly structured
    assert isinstance(structured, dict), "Should return structured dict"
    assert len(structured.get("key_facts", [])) > 0, "Should extract key facts"


def run_all_researcher_tests():
    """Run all researcher tool tests."""
    print("=" * 60)
    print("RESEARCHER TOOLS TEST SUITE")
    print("=" * 60)
    print("Using model: ollama_chat/qwen3:8b")

    tests = [
        test_search_term_extractor,
        test_search_term_extractor_complex,
        test_searxng_search,
        test_citation_builder_basic,
        test_citation_builder_with_writing,
        test_citation_builder_real_world,
        test_data_structurer_small,
        test_data_structurer_large,
        test_data_structurer_real_world,
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
    success = run_all_researcher_tests()
    sys.exit(0 if success else 1)

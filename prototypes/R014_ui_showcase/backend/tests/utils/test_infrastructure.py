#!/usr/bin/env python3
"""
Standalone tests for infrastructure modules.
Tests decision_tree, chunking, and validation modules.
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from services.core.decision_tree import (
    DecisionTree,
    ConditionNode,
    ActionNode,
    DecisionTreeBuilder,
)
from services.core.chunking import chunk_text, deduplicate_items
from services.core.validation import (
    validate_output,
    extract_list_from_text,
    parse_numbered_list,
    parse_float_score,
)


def test_decision_tree_simple():
    """Test simple binary decision tree."""
    print("\n=== Test: Decision Tree - Simple Binary ===")

    # Tree: Is number even? -> Yes/No branches
    tree = DecisionTree(
        root=ConditionNode(
            condition=lambda ctx: ctx["number"] % 2 == 0,
            true_branch=ActionNode(lambda ctx: {"result": "even"}, name="even"),
            false_branch=ActionNode(lambda ctx: {"result": "odd"}, name="odd"),
            name="is_even",
        )
    )

    # Test even
    result = tree.execute({"number": 4})
    assert result["result"] == "even", f"Expected 'even', got {result}"
    print("  ✓ Even number: 4 -> 'even'")

    # Test odd
    result = tree.execute({"number": 7})
    assert result["result"] == "odd", f"Expected 'odd', got {result}"
    print("  ✓ Odd number: 7 -> 'odd'")


def test_decision_tree_nested():
    """Test nested decision tree with multiple levels."""
    print("\n=== Test: Decision Tree - Nested Conditions ===")

    # Tree: Is positive? -> Is even? -> Yes/No/Positive/Negative
    tree = DecisionTree(
        root=ConditionNode(
            condition=lambda ctx: ctx["number"] > 0,
            true_branch=ConditionNode(
                condition=lambda ctx: ctx["number"] % 2 == 0,
                true_branch=ActionNode(
                    lambda ctx: {"result": "positive even"}, name="pos_even"
                ),
                false_branch=ActionNode(
                    lambda ctx: {"result": "positive odd"}, name="pos_odd"
                ),
                name="is_even",
            ),
            false_branch=ActionNode(lambda ctx: {"result": "negative"}, name="neg"),
            name="is_positive",
        )
    )

    tests = [
        (4, "positive even"),
        (7, "positive odd"),
        (-3, "negative"),
    ]

    for num, expected in tests:
        result = tree.execute({"number": num})
        assert result["result"] == expected, (
            f"{num}: Expected '{expected}', got {result}"
        )
        print(f"  ✓ {num} -> '{expected}'")


def test_decision_tree_builder():
    """Test fluent builder pattern for complex trees."""
    print("\n=== Test: Decision Tree Builder ===")

    # Build chart type decision tree
    builder = DecisionTreeBuilder()

    chart_tree = (
        builder.when(lambda ctx: ctx["data_type"] == "parts_of_whole")
        .then(lambda ctx: {"chart_type": "pie", "rationale": "Showing parts of whole"})
        .otherwise(
            DecisionTree(
                root=ConditionNode(
                    condition=lambda ctx: ctx["data_type"] == "time_series",
                    true_branch=ActionNode(
                        lambda ctx: {
                            "chart_type": "line",
                            "rationale": "Showing trends over time",
                        },
                        name="line",
                    ),
                    false_branch=ActionNode(
                        lambda ctx: {
                            "chart_type": "bar",
                            "rationale": "Comparing categories",
                        },
                        name="bar",
                    ),
                    name="is_time_series",
                )
            )
        )
        .build(lambda ctx: {"chart_type": "table", "rationale": "Default fallback"})
    )

    tests = [
        ({"data_type": "parts_of_whole"}, "pie"),
        ({"data_type": "time_series"}, "line"),
        ({"data_type": "categorical"}, "bar"),
        ({"data_type": "unknown"}, "table"),
    ]

    for ctx, expected_type in tests:
        result = chart_tree.execute(ctx)
        assert result["chart_type"] == expected_type, (
            f"Expected {expected_type}, got {result}"
        )
        print(
            f"  ✓ {ctx['data_type']} -> {result['chart_type']}: {result['rationale']}"
        )


def test_chunking_basic():
    """Test basic text chunking."""
    print("\n=== Test: Chunking - Basic ===")

    # Small text (no chunking)
    short = "This is short text."
    chunks = chunk_text(short, chunk_size=100, overlap=20)
    assert len(chunks) == 1, f"Short text should produce 1 chunk, got {len(chunks)}"
    print(f"  ✓ Short text ({len(short)} chars) -> 1 chunk")

    # Long text (chunked)
    long_text = " ".join([f"Word{i}" for i in range(100)])  # ~600 chars
    chunks = chunk_text(long_text, chunk_size=200, overlap=50)
    assert len(chunks) > 1, "Long text should produce multiple chunks"
    print(f"  ✓ Long text ({len(long_text)} chars) -> {len(chunks)} chunks")

    # Verify overlap
    if len(chunks) >= 2:
        chunk0_end = chunks[0][-50:]
        chunk1_start = chunks[1][:50]
        overlap_found = any(word in chunk1_start for word in chunk0_end.split())
        print(f"  ✓ Overlap detected between chunks 0 and 1: {overlap_found}")


def test_chunking_edge_cases():
    """Test chunking edge cases."""
    print("\n=== Test: Chunking - Edge Cases ===")

    # Empty string
    chunks = chunk_text("", chunk_size=100, overlap=20)
    assert chunks == [""], "Empty string should return ['']"

    # Exact chunk size
    exact = "a" * 100
    chunks = chunk_text(exact, chunk_size=100, overlap=20)
    assert len(chunks) == 1, f"Exact size should produce 1 chunk, got {len(chunks)}"
    print("  ✓ Exact chunk size -> 1 chunk")

    # One char over
    over = "a" * 101
    chunks = chunk_text(over, chunk_size=100, overlap=20)
    assert len(chunks) == 2, f"Over size should produce 2 chunks, got {len(chunks)}"
    print("  ✓ One char over -> 2 chunks")


def test_deduplication():
    """Test item deduplication."""
    print("\n=== Test: Deduplication ===")

    items = [
        "AI is transforming technology",
        "Machine learning is powerful",
        "AI is transforming technology",  # Duplicate
        "Deep learning is a subset",
        "machine learning is powerful",  # Case variation
        "Deep learning models",
        "  Extra spaces  ",  # Whitespace variation
        "Short",  # Below min length
        "",  # Empty
    ]

    unique = deduplicate_items(items, normalize=True, min_length=10)

    print(f"  Original: {len(items)} items")
    print(f"  Unique: {len(unique)} items")
    print(f"  Items: {unique}")

    # Verify no duplicates
    lower_unique = [u.lower() for u in unique]
    assert len(lower_unique) == len(set(lower_unique)), "Found duplicates"

    # Verify min length filter
    assert all(len(u) >= 10 for u in unique), "Found item below min length"

    print("  ✓ Deduplication working correctly")


def test_list_extraction():
    """Test various list formats from LLM output."""
    print("\n=== Test: List Extraction ===")

    test_cases = [
        ("item1, item2, item3", ["item1", "item2", "item3"], "Comma-separated"),
        ("- item1\n- item2\n- item3", ["item1", "item2", "item3"], "Bullet points"),
        ("1. item1\n2. item2\n3. item3", ["item1", "item2", "item3"], "Numbered list"),
        ("* item1\n* item2", ["item1", "item2"], "Asterisk bullets"),
        ("", [], "Empty string"),
    ]

    for text, expected, desc in test_cases:
        result = extract_list_from_text(text)
        assert result == expected, f"{desc}: Expected {expected}, got {result}"
        print(f"  ✓ {desc}: {result}")


def test_numbered_list_parsing():
    """Test numbered list parsing with various formats."""
    print("\n=== Test: Numbered List Parsing ===")

    test_cases = [
        ("1. First item\n2. Second item", ["First item", "Second item"], "Dot format"),
        (
            "1) First item\n2) Second item",
            ["First item", "Second item"],
            "Paren format",
        ),
        (
            "Mixed line\n1. Numbered\nAnother",
            ["Mixed line", "Numbered", "Another"],
            "Mixed format",
        ),
    ]

    for text, expected, desc in test_cases:
        result = parse_numbered_list(text)
        assert result == expected, f"{desc}: Expected {expected}, got {result}"
        print(f"  ✓ {desc}: {result}")


def test_float_score_parsing():
    """Test float score parsing with fallbacks."""
    print("\n=== Test: Float Score Parsing ===")

    test_cases = [
        ("0.75", 0.75, "Direct float"),
        ("The score is 0.85", 0.85, "Text wrapped"),
        ("75%", 0.75, "Percentage"),
        ("1.0", 1.0, "Max score"),
        ("0", 0.0, "Zero score"),
        ("High relevance", 0.8, "Qualitative high"),
        ("Medium quality", 0.5, "Qualitative medium"),
        ("Low relevance", 0.2, "Qualitative low"),
        ("", 0.0, "Empty string"),
        ("invalid", 0.0, "Invalid text"),
    ]

    for text, expected, desc in test_cases:
        result = parse_float_score(text, default=0.0)
        # Allow small tolerance for qualitative values
        if "qualitative" in desc:
            assert result >= expected - 0.1, (
                f"{desc}: Expected ~{expected}, got {result}"
            )
        else:
            assert result == expected, f"{desc}: Expected {expected}, got {result}"
        print(f"  ✓ {desc}: '{text}' -> {result}")


def test_validate_output():
    """Test output validation with fallback."""
    print("\n=== Test: Output Validation ===")

    # Valid output
    result = validate_output(
        output=[1, 2, 3],
        validator=lambda x: isinstance(x, list) and len(x) > 0,
        on_invalid=lambda: [],
    )
    assert result == [1, 2, 3], "Valid output should pass through"
    print("  ✓ Valid output passes through")

    # Invalid output with fallback
    result = validate_output(
        output=None,
        validator=lambda x: isinstance(x, list),
        on_invalid=lambda: ["fallback"],
    )
    assert result == ["fallback"], "Invalid output should trigger fallback"
    print("  ✓ Invalid output triggers fallback")

    # Invalid output without fallback
    result = validate_output(
        output=None,
        validator=lambda x: isinstance(x, list),
        on_invalid=None,
    )
    assert result is None, "Invalid output without fallback should return None"
    print("  ✓ Invalid output without fallback returns None")


def run_all_infrastructure_tests():
    """Run all infrastructure tests."""
    print("=" * 60)
    print("INFRASTRUCTURE MODULES TEST SUITE")
    print("=" * 60)

    tests = [
        test_decision_tree_simple,
        test_decision_tree_nested,
        test_decision_tree_builder,
        test_chunking_basic,
        test_chunking_edge_cases,
        test_deduplication,
        test_list_extraction,
        test_numbered_list_parsing,
        test_float_score_parsing,
        test_validate_output,
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
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_infrastructure_tests()
    sys.exit(0 if success else 1)

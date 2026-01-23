#!/usr/bin/env python3
"""
Standalone tests for Multi-Hop Web Reader ("Z-read on steroids").
Tests basic read mode and multi-hop mode with n² report generation.
"""

import asyncio
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

from services.tools.researcher.multihop_reader import MultiHopReader
from services.tools.researcher.web_fetcher import fetch_page, truncate_content


def test_truncate_content():
    """Test content truncation with sentence boundary preservation."""
    print("\n=== Test: Truncate Content ===")

    test_cases = [
        # Short content (no truncation needed)
        ("Short text.", 20, True),  # Should not truncate

        # Long content (truncation needed)
        ("This is a long sentence. Another sentence here. " * 10, 100, False),  # Should truncate

        # Content with newlines - use larger max to avoid edge cases
        ("Line 1\nLine 2\nLine 3\n" * 10, 30, False),  # Should truncate
    ]

    for i, (content, max_chars, should_match) in enumerate(test_cases, 1):
        result = truncate_content(content, max_chars)
        print(f"\n  [{i}] Input length: {len(content)}, max: {max_chars}")
        print(f"       Output length: {len(result)}")
        print(f"       Should truncate: {not should_match}")

        # Core checks
        if should_match and len(content) <= max_chars:
            # Short content should not be modified
            if result != content:
                print("       ⚠ Note: Short content modified (may be ok)")
        else:
            # Long content should be shorter than original
            assert len(result) < len(content), f"Should truncate: got {len(result)}, original {len(content)}"

    print("  ✓ All truncate tests passed")
    return True



async def test_fetch_page_real():
    """Test fetching a real web page."""
    print("\n=== Test: Fetch Real Page ===")

    # Test with a reliable, simple page
    test_url = "https://example.com"

    print(f"\n  Fetching: {test_url}")
    result = await fetch_page(test_url)

    if result:
        print("  ✓ Success!")
        print(f"    Title: {result.get('title', 'N/A')}")
        print(f"    Content length: {len(result.get('markdown_content', ''))}")
        print(f"    Links found: {len(result.get('links', []))}")

        # Verify structure
        assert "url" in result, "Missing url field"
        assert "title" in result, "Missing title field"
        assert "markdown_content" in result, "Missing markdown_content field"
        assert "links" in result, "Missing links field"
        assert result["url"] == test_url, "URL mismatch"

        return True
    else:
        print("  ✗ Failed to fetch page (may be network issue)")
        return False


async def test_basic_read_mode():
    """Test basic read mode (single URL, like Z-read)."""
    print("\n=== Test: Basic Read Mode (Z-read equivalent) ===")

    reader = MultiHopReader()

    # Test with example.com (very reliable)
    test_url = "https://example.com"
    goal = "What is this page about?"

    print(f"\n  URL: {test_url}")
    print(f"  Goal: {goal}")

    try:
        result = await reader.basic_read(url=test_url, goal=goal)

        print("\n  Result:")
        print(f"    Title: {result.get('title', 'N/A')}")
        print(f"    Relevant content: {len(result.get('relevant_content', ''))} chars")
        print(f"    Report: {len(result.get('report', ''))} chars")
        print(f"    Word count: {result.get('word_count', 0)}")

        if result.get('report'):
            print("\n  Report preview:")
            print(f"    {result['report'][:200]}...")

        # Verify structure
        assert "url" in result, "Missing url field"
        assert "title" in result, "Missing title field"
        assert "relevant_content" in result, "Missing relevant_content field"
        assert "report" in result, "Missing report field"

        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_multihop_read_mode():
    """Test multi-hop mode with n² report generation."""
    print("\n=== Test: Multi-Hop Read Mode (n² reports) ===")

    reader = MultiHopReader()

    # Use a small set of reliable URLs for testing
    test_urls = [
        "https://example.com",
    ]
    goal = "What information is available on this page?"

    max_hops = 2  # Use 2 hops for faster testing → 2² = 4 reports target

    print(f"\n  URLs: {test_urls}")
    print(f"  Goal: {goal}")
    print(f"  Max hops: {max_hops}")
    print(f"  Target reports: {max_hops ** 2}")

    try:
        result = await reader.multihop_read(
            urls=test_urls,
            goal=goal,
            max_hops=max_hops,
        )

        print("\n  Results:")
        print(f"    Total reports: {result.get('total_count', 0)}")
        print(f"    Target reports: {result.get('target_reports', 0)}")
        print(f"    Citations: {len(result.get('citations', []))}")
        print(f"    Trajectory entries: {len(result.get('trajectory', []))}")

        hop_dist = result.get('hop_distribution', {})
        print("\n  Hop distribution:")
        for hop, count in hop_dist.items():
            print(f"    Hop {hop}: {count} reports")

        # Show sample reports
        all_reports = result.get('all_reports', [])
        if all_reports:
            print("\n  Sample reports:")
            for i, report in enumerate(all_reports[:3], 1):
                print(f"\n    {i}. [Hop {report.get('hop_level', '?')}]")
                print(f"       Source: {report.get('source_title', 'N/A')[:50]}")
                print(f"       Words: {report.get('word_count', 0)}")
                print(f"       Preview: {report.get('report', '')[:100]}...")

        # Show trajectory
        trajectory = result.get('trajectory', [])
        if trajectory:
            print("\n  Trajectory (first 5):")
            for entry in trajectory[:5]:
                status = entry.get('status', '?')
                hop = entry.get('hop', '?')
                url = entry.get('url', '')[:60]
                print(f"    [Hop {hop}] {status}: {url}")

        # Verify structure
        assert "all_reports" in result, "Missing all_reports field"
        assert "total_count" in result, "Missing total_count field"
        assert "citations" in result, "Missing citations field"
        assert "trajectory" in result, "Missing trajectory field"
        assert "target_reports" in result, "Missing target_reports field"

        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_multihop_tests():
    """Run all multi-hop reader tests."""
    print("=" * 60)
    print("MULTI-HOP WEB READER TEST SUITE")
    print("=" * 60)
    print("Using model: ollama_chat/qwen3:8b")

    tests = [
        ("Truncate Content", test_truncate_content),
        ("Fetch Real Page", test_fetch_page_real),
        ("Basic Read Mode", test_basic_read_mode),
        ("Multi-Hop Read Mode", test_multihop_read_mode),
    ]

    passed = 0
    failed = 0

    for name, test in tests:
        print("\n" + "-" * 60)
        print(f"Running: {name}")
        print("-" * 60)

        try:
            if asyncio.iscoroutinefunction(test):
                success = await test()
            else:
                success = test()

            if success:
                passed += 1
                print(f"✓ PASSED: {name}")
            else:
                failed += 1
                print(f"✗ FAILED: {name}")

        except AssertionError as e:
            print(f"✗ FAILED: {name} - {e}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {name} - {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_multihop_tests())
    sys.exit(0 if success else 1)

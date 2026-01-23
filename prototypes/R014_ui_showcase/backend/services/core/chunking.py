# =============================================================================
# AGENTX Chunking Infrastructure
# =============================================================================
# Text chunking utilities for processing large inputs in smaller pieces
# =============================================================================

from typing import List, Callable, TypeVar

T = TypeVar("T")


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks.

    Args:
        text: Full text to chunk
        chunk_size: Target chunk size in characters
        overlap: Overlap between chunks

    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start = end - overlap if end < len(text) else len(text)
    return chunks


def chunk_list(items: List[T], chunk_size: int) -> List[List[T]]:
    """Split a list into chunks.

    Args:
        items: List to chunk
        chunk_size: Items per chunk

    Returns:
        List of item chunks
    """
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]


def deduplicate_items(
    items: List[str], normalize: bool = True, min_length: int = 10
) -> List[str]:
    """Remove duplicate items from a list.

    Args:
        items: List of items to deduplicate
        normalize: Whether to normalize (lowercase, strip) before comparison
        min_length: Minimum item length to keep

    Returns:
        Unique items
    """
    seen = set()
    unique = []
    for item in items:
        if not item or len(item) < min_length:
            continue
        key = item.lower().strip() if normalize else item
        if key and key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def iterative_refine(
    items: List[T],
    processor: Callable[[List[T], List[T]], List[T]],
    iterations: int = 3,
) -> List[T]:
    """Run processor iteratively, feeding results back in.

    Args:
        items: Initial items
        processor: Function that takes (current_items, previous_items) and returns new_items
        iterations: Number of iterations to run

    Returns:
        Refined items after all iterations
    """
    current = items
    previous: List[T] = []

    for i in range(iterations):
        current = processor(current, previous)
        previous = current

    return current

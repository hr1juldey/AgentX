"""Memory retrieval tools for DSPy agents."""

import dspy


def retrieve_memory(query: str, user_id: str) -> str:
    """Retrieve relevant memories for the query.

    Args:
        query: Query to search for
        user_id: User identifier

    Returns:
        Retrieved memories as string

    Raises:
        NotImplementedError: If not yet implemented
    """
    raise NotImplementedError("retrieve_memory() not yet implemented")


# Create DSPy tool wrapper
retrieve_memory_tool = dspy.Tool(retrieve_memory, name="retrieve_memory")

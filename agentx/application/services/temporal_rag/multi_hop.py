"""Multi-hop search for temporal RAG.

Handles multi-hop retrieval for complex queries.
"""

from agentx.infrastructure.database.qdrant_vector_store import QdrantVectorStore


async def multi_hop_search(
    vector_store: QdrantVectorStore,
    queries: list[str],
    user_id: str,
    tier: int = 3,
    limit_per_hop: int = 3,
) -> list[dict]:
    """Multi-hop retrieval for complex queries.

    Args:
        vector_store: Qdrant vector store instance.
        queries: List of queries for each hop.
        user_id: User identifier.
        tier: Memory tier to search.
        limit_per_hop: Results per hop.

    Returns:
        list[dict]: Consolidated multi-hop results.
    """
    all_results = {}
    seen_ids = set()

    for query in queries:
        results = await vector_store.search_memories(
            query=query,
            user_id=user_id,
            tier=tier,
            limit=limit_per_hop,
        )

        for result in results:
            memory_id = str(result.get("memory_id"))
            if memory_id not in seen_ids:
                seen_ids.add(memory_id)
                all_results[memory_id] = result

    return list(all_results.values())

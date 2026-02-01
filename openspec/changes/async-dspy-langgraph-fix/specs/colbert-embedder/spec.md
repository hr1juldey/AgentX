# Spec: ColBERT Embedder

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Draft

---

## 1. Purpose

Define the ColBERTv2 embedder for token-level semantic search with multivectors.

**Success Criteria**:
- ColBERTEmbedder class with lazy-loading
- Multivector embeddings (128-dim per token)
- Qdrant collection with MultiVectorConfig
- Semantic search with MaxSim operation

---

## 2. Scope

### In Scope

- ColBERTEmbedder class
- Multivector embedding generation
- Qdrant collection configuration
- Semantic search with user filtering

### Out of Scope

- Qdrant client setup (external dependency)
- Store integration (covered by agent-memory-store spec)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-CE-001 | ColBERTEmbedder MUST lazy-load model | Must |
| FR-CE-002 | MUST generate multivector embeddings | Must |
| FR-CE-003 | MUST support query optimization | Should |
| FR-CE-004 | MUST enforce user isolation | Must |

### 3.2 Non-Functional Requirements

| ID | Requirement | Target Metric |
|----|-------------|---------------|
| NFR-CE-001 | Model size | ~440MB (lazy-loaded) |
| NFR-CE-002 | Embedding latency | < 2s per document |

---

## 4. Data Model

```python
# infrastructure/external/colbert_embedder.py
from fastembed import LateInteractionTextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, MultiVectorConfig, MultiVectorComparator, Distance

class ColBERTEmbedder:
    """ColBERTv2 late interaction embedder for semantic search.

    Why ColBERT?
    - Token-level granularity (preserves fine-grained semantics)
    - Late interaction (efficient MaxSim operation)
    - Multivector output (each token → 128-dim vector)
    - State-of-the-art retrieval performance
    """

    MODEL_NAME = "colbert-ir/colbertv2.0"  # 128 dimensions per token
    VECTOR_SIZE = 128

    def __init__(self, qdrant_url: str = "http://localhost:6333"):
        self._embedder: LateInteractionTextEmbedding | None = None
        self.client = QdrantClient(url=qdrant_url)
```

---

## 5. API Contract

```python
class ColBERTEmbedder:
    # ... (see above)

    @property
    def embedder(self) -> LateInteractionTextEmbedding:
        """Lazy-load ColBERT model (expensive, ~440MB)."""
        if self._embedder is None:
            self._embedder = LateInteractionTextEmbedding(
                model_name=self.MODEL_NAME,
            )
        return self._embedder

    def embed_text(self, text: str) -> list[list[float]]:
        """Embed text as multivectors (one vector per token).

        Args:
            text: Text to embed

        Returns:
            list[list[float]]: Multivector embedding (num_tokens × 128)
        """
        # embed() returns generator of multivectors
        embeddings = list(self.embedder.embed([text]))
        return embeddings[0]  # First (and only) text

    def query_embed(self, query: str) -> list[list[float]]:
        """Embed query for search (optimized for retrieval).

        Args:
            query: Search query

        Returns:
            list[list[float]]: Optimized query embedding
        """
        # query_embed() is optimized for search queries
        embeddings = list(self.embedder.query_embed([query]))
        return embeddings[0]

    def ensure_collection(self, collection_name: str) -> None:
        """Create Qdrant collection with multivector config.

        Args:
            collection_name: Name of collection to create
        """
        collections = [c.name for c in self.client.get_collections().collections]
        if collection_name not in collections:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=Distance.COSINE,
                    multivector_config=MultiVectorConfig(
                        comparator=MultiVectorComparator.MAX_SIM  # MaxSim operation
                    ),
                ),
            )

    async def search(
        self,
        collection_name: str,
        query: str,
        limit: int = 10,
        user_id: str = None,
    ) -> list[dict]:
        """Semantic search using ColBERT late interaction.

        Args:
            collection_name: Qdrant collection name
            query: Search query
            limit: Max results
            user_id: Optional filter for user isolation

        Returns:
            list[dict]: Search results with scores
        """
        query_vectors = self.query_embed(query)

        # Build filter (user isolation)
        query_filter = None
        if user_id:
            from qdrant_client.models import Filter, FieldCondition
            query_filter = Filter(
                must=[FieldCondition(key="user_id", match={"value": user_id})]
            )

        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vectors,
            limit=limit,
            query_filter=query_filter,
        )

        return [
            {
                "content": r.payload.get("content", ""),
                "score": r.score,
                "metadata": {
                    k: v for k, v in r.payload.items()
                    if k not in ["content", "_id"]
                },
            }
            for r in results
        ]
```

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-CE-001 | Lazy-load on first use | @property with None check |
| BR-CE-002 | User isolation required | user_id filter |
| BR-CE-003 | MaxSim comparator | MultiVectorComparator.MAX_SIM |

---

## 7. Acceptance Criteria

- [ ] ColBERTEmbedder class created
- [ ] Model lazy-loads (not at __init__)
- [ ] Multivector embeddings work (list of lists)
- [ ] Qdrant collection with MultiVectorConfig
- [ ] Semantic search returns relevant results
- [ ] User filter enforced
- [ ] Ruff and pyrefly checks pass

---

## 8. Test Scenarios

| Query | Expected Results |
|-------|-----------------|
| "climate change" | Climate-related documents |
| "python programming" | Python docs, tutorials |
| Same query, different user_id | Only that user's documents |

---

**Next**: See `agent-memory-store/spec.md` for Store integration.

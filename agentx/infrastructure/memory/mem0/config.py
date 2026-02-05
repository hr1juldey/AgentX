"""Mem0AI configuration builder."""


def build_mem0_config(
    qdrant_host: str,
    qdrant_port: int,
    llm_model: str,
    embedder_model: str,
    embedding_dims: int,
) -> dict:
    """Build Mem0AI configuration for local Ollama + Qdrant setup.

    Args:
        qdrant_host: Qdrant server host
        qdrant_port: Qdrant server port
        llm_model: Ollama LLM model name
        embedder_model: Ollama embedding model name
        embedding_dims: Embedding vector dimensions

    Returns:
        Configuration dict for Mem0AI Memory.from_config()
    """
    return {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "collection_name": "agentx_memories",
                "host": qdrant_host,
                "port": qdrant_port,
                "embedding_model_dims": embedding_dims,
            },
        },
        "llm": {
            "provider": "ollama",
            "config": {
                "model": llm_model,
                "temperature": 0,
                "ollama_base_url": "http://localhost:11434",
            },
        },
        "embedder": {
            "provider": "ollama",
            "config": {
                "model": embedder_model,
                "ollama_base_url": "http://localhost:11434",
            },
        },
    }

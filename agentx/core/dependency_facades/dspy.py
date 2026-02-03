"""DSPy configuration dependency.

Provides DSPy LM + RM configuration with Ollama and Mem0 retrieval.
Fixes Fraud #3.7: DSPy configure never sets retrieval model (RM).
"""

import dspy

from agentx.core.config import get_settings
from agentx.infrastructure.retrieval.mem0_dspy_retriever import Mem0DSPyRetriever

# Global singleton state
_dspy_configured: bool = False
_retriever_initialized: bool = False


def configure_dspy() -> None:
    """Configure DSPy with Ollama LM and Mem0 retriever RM.

    Uses settings from config.py. Must be called before any DSPy agent usage.

    FIX: Now configures both LM (language model) and RM (retrieval model).
    """
    global _dspy_configured, _retriever_initialized
    if _dspy_configured:
        return

    settings = get_settings()

    # Configure LM (Language Model)
    lm = dspy.LM(
        model=f"ollama_chat/{settings.llm.model}",
        api_base=settings.llm.api_base,
        api_key="",  # Ollama doesn't require API key, but DSPy needs empty string
        temperature=settings.llm.temperature,
        max_tokens=settings.llm.max_tokens,
        cache=True,  # Enable caching for performance
    )

    # Configure RM (Retrieval Model) - FIX: Add this for DSPy retrieval
    retriever = Mem0DSPyRetriever(k=10, quality_threshold=0.6, min_results=3)

    # Configure DSPy with both LM and RM
    dspy.configure(lm=lm, rm=retriever)  # FIX: Add RM parameter
    _dspy_configured = True
    _retriever_initialized = True


def ensure_dspy_configured() -> None:
    """Ensure DSPy is configured with Ollama LM.

    This should be called before any DSPy agent usage.
    """
    configure_dspy()


def reset_dspy() -> None:
    """Reset DSPy configuration singleton.

    Useful for testing or clearing state.
    """
    global _dspy_configured
    _dspy_configured = False

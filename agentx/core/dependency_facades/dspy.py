"""DSPy configuration dependency.

Provides DSPy LM + RM configuration with Ollama and Mem0 retrieval.
Fixes Fraud #3.7: DSPy configure never sets retrieval model (RM).
Fixes Fraud #5.8: No DSPy optimizer configured.
"""

import dspy
from typing import Any

from agentx.core.config import get_settings
from agentx.infrastructure.retrieval.mem0_dspy_retriever import Mem0DSPyRetriever

# Global singleton state
_dspy_configured: bool = False
_retriever_initialized: bool = False

# Optimizer configuration (Fraud #5.8)
DEFAULT_MAX_BOOSTROUNDS: int = 3
DEFAULT_MAX_Labeled_Demos: int = 4
DEFAULT_MAX_TRexamples: int = 2


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


def optimize_module_with_bootstrap(
    module: dspy.Module,
    trainset: list[dspy.Example],
    max_bootstrapped_demos: int = DEFAULT_MAX_Labeled_Demos,
    max_labeled_demos: int = DEFAULT_MAX_TRexamples,
    max_rounds: int = DEFAULT_MAX_BOOSTROUNDS,
) -> dspy.Module:
    """Optimize a DSPy module using BootstrapFewShot optimizer.

    Phase 3 Fix: Added optimizer support (Fraud #5.8).

    Args:
        module: The DSPy module to optimize (e.g., RAGContextGenerator, MainDSPyReActAgent)
        trainset: Training examples (list of dspy.Example with inputs and outputs)
        max_bootstrapped_demos: Maximum number of bootstrapped demos to generate
        max_labeled_demos: Maximum number of labeled demos to use from trainset
        max_rounds: Maximum optimization rounds

    Returns:
        Optimized DSPy module (same instance, compiled)

    Example:
        >>> # Create training examples
        >>> trainset = [
        ...     dspy.Example(query="What is X?", answer="X is...").with_inputs("query"),
        ...     dspy.Example(query="How to Y?", answer="To Y...").with_inputs("query"),
        ... ]
        >>> # Optimize RAG agent
        >>> rag_agent = RAGContextGenerator()
        >>> optimized_rag = optimize_module_with_bootstrap(rag_agent, trainset)
    """
    ensure_dspy_configured()

    # Create BootstrapFewShot optimizer
    optimizer = dspy.BootstrapFewShot(
        max_bootstrapped_demos=max_bootstrapped_demos,
        max_labeled_demos=max_labeled_demos,
        max_rounds=max_rounds,
        teacher_settings=dict(lm=dspy.settings.lm),  # Use same LM for teacher
    )

    # Compile (optimize) the module
    optimized = optimizer.compile(module, trainset=trainset)
    return optimized


def optimize_module_with_random_search(
    module: dspy.Module,
    trainset: list[dspy.Example],
    metric: Any | None = None,
    max_bootstrapped_demos: int = DEFAULT_MAX_Labeled_Demos,
    max_labeled_demos: int = DEFAULT_MAX_TRexamples,
    num_candidate_programs: int = 5,
    num_threads: int = 4,
) -> dspy.Module:
    """Optimize a DSPy module using BootstrapFewShotWithRandomSearch optimizer.

    Phase 3 Fix: Added optimizer support (Fraud #5.8).

    Args:
        module: The DSPy module to optimize
        trainset: Training examples (list of dspy.Example with inputs and outputs)
        metric: Optional metric function for evaluation (defaults to None)
        max_bootstrapped_demos: Maximum number of bootstrapped demos to generate
        max_labeled_demos: Maximum number of labeled demos to use from trainset
        num_candidate_programs: Number of candidate programs to generate
        num_threads: Number of threads for parallel optimization

    Returns:
        Optimized DSPy module (same instance, compiled)

    Note:
        If metric is None, a simple answer_exact_match metric will be used.
    """
    ensure_dspy_configured()

    # Use default metric if none provided
    if metric is None:
        metric = dspy.evaluate.answer_exact_match

    optimizer = dspy.BootstrapFewShotWithRandomSearch(
        metric=metric,
        max_bootstrapped_demos=max_bootstrapped_demos,
        max_labeled_demos=max_labeled_demos,
        num_candidate_programs=num_candidate_programs,
        num_threads=num_threads,
        teacher_settings=dict(lm=dspy.settings.lm),
    )

    optimized = optimizer.compile(module, trainset=trainset)
    return optimized

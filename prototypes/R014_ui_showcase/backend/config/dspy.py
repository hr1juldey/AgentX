# =============================================================================
# AGENTX R014 - DSPy Configuration
# =============================================================================
# Centralized DSPy LLM configuration
# =============================================================================

import dspy

from config.settings import settings


def get_dspy_lm() -> dspy.LM:
    """Get configured DSPy Language Model based on environment settings.

    This function creates the appropriate DSPy LM based on the LLM_PROVIDER
    environment variable. Supports:
    - ollama: Local models via Ollama (default)
    - openai: OpenAI API (GPT-4, GPT-3.5, etc.)
    - anthropic: Anthropic API (Claude)

    Returns:
        Configured dspy.LM instance

    Raises:
        ValueError: If LLM provider is not supported
    """
    provider = settings.llm_provider.lower()
    model = settings.llm_model

    if provider == "ollama":
        # Ollama requires "ollama_chat/" prefix for chat models
        model_name = (
            f"ollama_chat/{model}" if not model.startswith("ollama_chat/") else model
        )
        return dspy.LM(
            model=model_name,
            api_base=settings.ollama_base_url,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )

    elif provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY must be set when using OpenAI provider")
        return dspy.LM(
            model=f"openai/{model}",
            api_key=settings.openai_api_key,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )

    elif provider == "anthropic":
        if not settings.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY must be set when using Anthropic provider"
            )
        return dspy.LM(
            model=f"anthropic/{model}",
            api_key=settings.anthropic_api_key,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )

    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}. "
            f"Supported providers: ollama, openai, anthropic"
        )


def configure_dspy() -> None:
    """Configure DSPy with the LLM from environment settings.

    This should be called once at application startup (e.g., in routes.py).
    After calling this, all DSPy modules will use the configured LM.
    """
    lm = get_dspy_lm()
    dspy.configure(lm=lm)


# =============================================================================
# Convenience function for getting current LM info
# =============================================================================


def get_lm_info() -> dict[str, str]:
    """Get information about the current LLM configuration.

    Returns:
        Dict with provider, model, and configuration details
    """
    return {
        "provider": settings.llm_provider,
        "model": settings.llm_model,
        "temperature": str(settings.llm_temperature),
        "max_tokens": str(settings.llm_max_tokens),
        "api_base": settings.ollama_base_url
        if settings.llm_provider == "ollama"
        else "N/A",
    }

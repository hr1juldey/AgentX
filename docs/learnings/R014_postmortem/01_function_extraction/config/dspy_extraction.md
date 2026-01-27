# Function Postmortem: config/dspy.py

## Metadata
- **File**: config/dspy.py
- **Lines of Code**: 101
- **Purpose**: Centralized DSPy LLM configuration
- **Dependencies**: `dspy`, `config.settings`

---

## Analysis

**File Status**: PRODUCTION CONFIGURATION

**Purpose**: Centralized DSPy Language Model configuration supporting multiple providers (Ollama, OpenAI, Anthropic).

---

## Functions Extracted

### get_dspy_lm

**Purpose**: Get configured DSPy Language Model based on environment settings

**Signature**:
```python
def get_dspy_lm() -> dspy.LM:
```

**Lines**: 12-68

**Complexity**: O(1) - conditional logic

**Key Code**:
```python
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
```

**What Works**:
- ✅ Provider abstraction (Ollama, OpenAI, Anthropic)
- ✅ Ollama chat prefix handling
- ✅ API key validation
- ✅ Temperature and max_tokens configuration
- ✅ Clear error messages

**Mistakes Found**:
- ⚠️ Only 3 providers supported (could add more)
- ⚠️ No retry logic for API failures

**Behavioral Notes**:
- Ollama: Adds "ollama_chat/" prefix if not present
- OpenAI/Anthropic: Validates API key exists
- Raises ValueError for unsupported providers

**Reusability**: HIGH - Multi-provider DSPy configuration

---

### configure_dspy

**Purpose**: Configure DSPy with the LLM from environment settings

**Signature**:
```python
def configure_dspy() -> None:
```

**Lines**: 71-78

**Key Code**:
```python
def configure_dspy() -> None:
    """Configure DSPy with the LLM from environment settings.

    This should be called once at application startup (e.g., in routes.py).
    After calling this, all DSPy modules will use the configured LM.
    """
    lm = get_dspy_lm()
    dspy.configure(lm=lm)
```

**What Works**:
- ✅ Simple configuration function
- ✅ Should be called once at startup
- ✅ Global DSPy configuration

**Mistakes Found**: None

**Reusability**: HIGH - Standard DSPy configuration pattern

---

### get_lm_info

**Purpose**: Get information about the current LLM configuration

**Signature**:
```python
def get_lm_info() -> dict[str, str]:
```

**Lines**: 86-100

**Key Code**:
```python
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
```

**What Works**:
- ✅ Returns all key configuration
- ✅ Provider-specific details (api_base for Ollama)
- ✅ Useful for debugging/logging

**Mistakes Found**: None

**Reusability**: HIGH - Debugging and monitoring

---

## File Summary

**Total Classes**: 0
**Total Functions**: 3
**Lines of Code**: 101

**Violations**: None

**Success Patterns**:
- ✅ Provider abstraction (multiple LLM providers)
- ✅ Ollama chat prefix handling
- ✅ API key validation
- ✅ Centralized DSPy configuration
- ✅ Configuration info function for debugging

**Overall Assessment**: EXCELLENT - Clean multi-provider DSPy configuration.

**Key Learnings for Real AgentX**:
1. ✅ **Provider Abstraction**: Support multiple LLM providers from day 1
2. ✅ **Ollama Prefix**: Use "ollama_chat/" prefix for chat models
3. ✅ **API Key Validation**: Raise clear errors for missing keys
4. ✅ **Centralized Configuration**: Single `configure_dspy()` call
5. ✅ **Configuration Info**: Useful for debugging and monitoring

**Reuse for Real AgentX**: ✅ REQUIRED - Use this multi-provider pattern.

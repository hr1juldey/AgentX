# Function Postmortem: config/settings.py

## Metadata
- **File**: config/settings.py
- **Lines of Code**: 97
- **Purpose**: Pydantic Settings for environment-based configuration
- **Dependencies**: `functools.lru_cache`, `pydantic_settings`

---

## Analysis

**File Status**: PRODUCTION CONFIGURATION

**Purpose**: Centralized application settings loaded from environment variables using Pydantic Settings.

---

## Classes Extracted

### Settings

**Purpose**: Application settings loaded from environment variables

**Signature**:
```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(...)
```

**Lines**: 12-86

**Configuration**:
```python
class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "R014 UI Showcase"
    app_version: str = "0.1.0"
    debug: bool = True
    mock_mode: bool = False
    log_level: str = "INFO"

    # Server
    host: str = "0.0.0.0"
    port: int = 8014

    # Database
    database_url: str = "sqlite:///./data/database.db"

    # CORS
    frontend_url: str = "http://localhost:3014"
    cors_origins: str = ""

    # LLM Configuration
    llm_provider: str = "ollama"
    llm_model: str = "gemma3:4b"
    ollama_base_url: str = "http://localhost:11434"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2048

    # Multi-Hop Search Configuration
    searxng_url: str = "http://192.168.1.4:8080"
    searxng_timeout: float = 10.0
    max_hops: int = 5
    docs_per_hop: int = 5
    stop_threshold: float = 0.85
    max_results: int = 25
    max_concurrent: int = 4

    # Async Configuration
    force_async: bool = False
    force_sync: bool = False
```

**What Works**:
- ✅ Pydantic Settings v2 pattern (`model_config`)
- ✅ Environment variable loading
- ✅ Type validation
- ✅ Default values provided
- ✅ Grouped by purpose (Application, Server, LLM, Search, Async)
- ✅ Mock mode support for testing

**Mistakes Found**:
- ⚠️ **Hardcoded SearXNG URL**: `http://192.168.1.4:8080` should be configurable
- ⚠️ **Hardcoded port**: 8014, 3014 are specific to this prototype
- ⚠️ **SQLite database**: Not production-ready

**Behavioral Notes**:
- `extra="ignore"` ignores unknown environment variables
- `case_sensitive=False` allows `APP_NAME` or `app_name`
- `.env` file loaded automatically

**Reusability**: HIGH - Settings pattern is reusable

---

## Functions Extracted

### get_settings

**Purpose**: Get cached settings instance

**Signature**:
```python
@lru_cache
def get_settings() -> Settings:
```

**Lines**: 89-92

**Key Code**:
```python
@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
```

**What Works**:
- ✅ LRU cache prevents re-parsing environment
- ✅ Singleton pattern
- ✅ Fast access after first call

**Mistakes Found**: None

**Reusability**: HIGH - Cached singleton pattern

---

## File Summary

**Total Classes**: 1
**Total Functions**: 1 (cached getter)
**Lines of Code**: 97

**Violations**: None

**Success Patterns**:
- ✅ Pydantic Settings v2 pattern
- ✅ Environment-based configuration
- ✅ Grouped settings by purpose
- ✅ Type validation with defaults
- ✅ Mock mode support
- ✅ Multiple LLM provider support (Ollama, OpenAI, Anthropic)

**Overall Assessment**: EXCELLENT - Clean configuration management with Pydantic Settings v2.

**Key Learnings for Real AgentX**:
1. ✅ **Pydantic Settings**: Use `model_config = SettingsConfigDict(...)` for v2
2. ✅ **Environment Groups**: Group related settings (LLM, Database, CORS)
3. ✅ **Mock Mode**: Include from day 1 for testing
4. ✅ **Provider Abstraction**: Support multiple LLM providers
5. ⚠️ **Avoid Hardcoded URLs**: Make SearXNG URL configurable
6. ⚠️ **Use Environment Variables**: For all external URLs and ports

**Reuse for Real AgentX**: ✅ REQUIRED - Use this settings pattern.

# Function Postmortem: main.py

## Metadata
- **File**: prototypes/R014_ui_showcase/backend/main.py
- **Lines of Code**: 97
- **Purpose**: FastAPI application entry point with lifespan management
- **Dependencies**: fastapi, uvicorn, api.routes, config.settings

---

## Analysis

**Status**: Working FastAPI application template

**Purpose**: Application entry point that configures FastAPI with CORS, lifespan management, and route inclusion.

**Architecture**: Standard FastAPI app factory pattern

---

## Functions/Classes Extracted

### lifespan (async context manager)

**Purpose**: Application lifespan manager

**Signature**: `async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]`

**Lines**: 27-43

**Key Code**:
```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info(f"{settings.app_name} v{settings.app_version} starting on {settings.host}:{settings.port}")
    logger.info(f"LLM: {settings.llm_provider}/{settings.llm_model}")

    # Configure DSPy with LLM
    from config.dspy import configure_dspy
    configure_dspy()

    yield
    # Shutdown
    logger.info("Shutting down...")
```

**What Works**:
- Clean startup/shutdown logging
- DSPy configuration on startup
- Proper context manager pattern

**Mistakes Found**:
- None - good implementation

**Dependencies**:
- FastAPI
- config.dspy.configure_dspy

**Reusability**: HIGH - Standard lifespan pattern

---

### app (FastAPI instance)

**Purpose**: Main FastAPI application

**Lines**: 46-52

```python
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=f"{settings.app_name} API",
    lifespan=lifespan,
)
```

---

### CORS Configuration

**Lines**: 54-68

```python
allowed_origins = [settings.frontend_url, "http://localhost:3014"]
if settings.cors_origins:
    allowed_origins.extend([origin.strip() for origin in settings.cors_origins.split(",")])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**What Works**:
- Frontend URL from settings
- Comma-separated origins support
- Permissive methods/headers

**Mistakes Found**:
- Very permissive CORS (allow all methods/headers)

---

### root (GET endpoint)

**Purpose**: Root health check endpoint

**Signature**: `async def root() -> dict[str, str]`

**Lines**: 74-81

```python
@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint for health check."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }
```

---

### main (function)

**Purpose**: Run the application server

**Signature**: `def main() -> None`

**Lines**: 84-92

```python
def main() -> None:
    """Run the application server."""
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        reload_excludes=["tests/*", "tests/*.*", ".pytest_cache/*", "*.pyc"],
    )
```

**What Works**:
- Settings-based configuration
- Debug mode controlled by settings
- Reload exclusions prevent issues

**Reusability**: HIGH - Standard uvicorn.run pattern

---

## File Summary

**Assessment**: Well-structured FastAPI application template. Good use of lifespan, CORS, and settings.

**Key Learnings**:
1. Lifespan context manager is proper pattern for startup/shutdown
2. DSPy configuration should happen in lifespan
3. CORS origins should be configurable
4. Uvicorn reload exclusions prevent issues with test files

**Mistakes to Avoid**:
1. Don't use overly permissive CORS in production
2. Don't forget to configure DSPy before use

**Recommendations**:
1. Tighten CORS for production
2. Add health check endpoint
3. Consider middleware for request logging

**Reusability Score**: HIGH - Excellent FastAPI template

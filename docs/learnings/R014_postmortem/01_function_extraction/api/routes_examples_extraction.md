# Function Postmortem: api/routes_examples.py

## Metadata
- **File**: prototypes/R014_ui_showcase/backend/api/routes_examples.py
- **Lines of Code**: 139
- **Purpose**: Static mock data endpoints for UI showcase
- **Dependencies**: fastapi, api.models

---

## Analysis

**Status**: Working example data endpoints for development/showcase

**Purpose**: Provides static mock data for UI components without needing LLM calls. Useful for frontend development and demos.

**Architecture**: Simple REST router with GET endpoints

---

## Functions/Classes Extracted

### get_example_descriptors (GET endpoint)

**Purpose**: Get static example UI descriptors

**Signature**: `async def get_example_descriptors() -> list[UIDescriptor]`

**Lines**: 22-88

**Key Code**:
```python
@router.get("/mock/descriptors")
async def get_example_descriptors() -> list[UIDescriptor]:
    return [
        UIDescriptor(
            id="markdown-1",
            type="markdown",
            content="# Welcome to AGENTX UI Showcase...",
            metadata={"format": "markdown"},
        ),
        UIDescriptor(
            id="card-1",
            type="card",
            title="About This Showcase",
            content="UI descriptors are **static** (7 fixed types)...",
            metadata={"icon": "info", "actions": [...]},
        ),
        # ... more widgets
    ]
```

**What Works**:
- Provides working examples out of the box
- Good variety of widget types
- Static data is reliable
- No external dependencies

**Mistakes Found**:
- All timestamps are `datetime.now()` - not stable
- IDs are hardcoded - could collide

**Reusability**: HIGH - Good for demos and development

---

### list_descriptor_types (GET endpoint)

**Purpose**: List all available descriptor types

**Signature**: `async def list_descriptor_types() -> list[str]`

**Lines**: 91-94

```python
@router.get("/mock/descriptors/types/list")
async def list_descriptor_types() -> list[str]:
    return ["markdown", "card", "form", "progress", "action", "confirmation", "voice"]
```

**Reusability**: HIGH - Useful for frontend type discovery

---

### get_past_sessions (GET endpoint)

**Purpose**: Get example past sessions

**Signature**: `async def get_past_sessions() -> list[dict[str, Any]]`

**Lines**: 97-115

```python
@router.get("/mock/sessions")
async def get_past_sessions() -> list[dict[str, Any]]:
    return [
        {
            "id": "session-1",
            "title": "Content Generation Tests",
            "date": datetime.now().isoformat(),
            "summary": "Generated various content types...",
            "widget_count": 6,
        },
        # ... more sessions
    ]
```

**Reusability**: MEDIUM - Specific to session UI

---

### get_data_connectors (GET endpoint)

**Purpose**: Get data connectors status

**Signature**: `async def get_data_connectors() -> list[dict[str, Any]]`

**Lines**: 118-138

```python
@router.get("/mock/connectors")
async def get_data_connectors() -> list[dict[str, Any]]:
    return [
        {
            "id": "ollama",
            "name": "Ollama LLM",
            "type": "llm",
            "status": "connected",
            "url": "http://localhost:11434",
            "description": "Local LLM (gemma3:4b) - Generates widget content",
        },
        {
            "id": "dspy",
            "name": "DSPy Framework",
            "type": "framework",
            "status": "connected",
            "url": "https://github.com/stanfordnlp/dspy",
            "description": "Programmatic LLM interface - Content generation",
        },
    ]
```

**Reusability**: HIGH - Good for status UI

---

## File Summary

**Assessment**: Simple but effective example data provider. Good for frontend development without backend dependencies.

**Key Learnings**:
1. Static mock data enables frontend development
2. Example endpoints are valuable for onboarding
3. Type discovery helps frontend validation
4. Connector status is useful for debugging

**Mistakes to Avoid**:
1. Don't use `datetime.now()` in static data
2. Don't hardcode IDs that could collide

**Recommendations**:
1. Use fixed timestamps for stability
2. Add UUID-based IDs
3. Consider JSON file for data source

**Reusability Score**: HIGH - Excellent for development/demos

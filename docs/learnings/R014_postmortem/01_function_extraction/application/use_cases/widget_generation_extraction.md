# Function Postmortem: application/use_cases/widget_generation.py

## Metadata
- **File**: application/use_cases/widget_generation.py
- **Lines of Code**: 76
- **Purpose**: Widget generation use cases (Clean Architecture facade)
- **Dependencies**: `domain.entities.ui_descriptor`, `services.widget_spawner`

---

## Analysis

**File Status**: CLEAN ARCHITECTURE USE CASE LAYER

**Purpose**: Use case facades that wrap existing services for clean architecture. Returns domain entities, not DTOs.

---

## Classes Extracted

### WidgetGenerationUseCase

**Purpose**: Use case for widget generation operations

**Signature**:
```python
class WidgetGenerationUseCase:
```

**Lines**: 11-64

**Architecture**: Facade pattern over WidgetSpawnerService

---

### generate_widget

**Purpose**: Generate widgets based on prompt and optional widget type

**Signature**:
```python
async def generate_widget(
    self, request: GenerateWidgetRequest
) -> list[UIDescriptor]:
```

**Lines**: 20-35

**Complexity**: O(n) where n is number of widgets generated

**Key Code**:
```python
async def generate_widget(
    self, request: GenerateWidgetRequest
) -> list[UIDescriptor]:
    """Generate widgets based on prompt and optional widget type.

    Returns domain entities (UIDescriptor).
    """
    from services.widget_spawner import get_widget_spawner_service

    service = get_widget_spawner_service()
    result = await service.generate_widget(
        prompt=request.prompt, widget_type=request.widget_type
    )

    # Convert service response to domain entities
    return [UIDescriptor(**widget.model_dump()) for widget in result.widgets]
```

**What Works**:
- ✅ Facade pattern (wraps WidgetSpawnerService)
- ✅ Returns domain entities (UIDescriptor)
- ✅ Async method
- ✅ Lazy import (from inside function)
- ✅ List comprehension for conversion

**Mistakes Found**: None

**Behavioral Notes**:
- Delegates to WidgetSpawnerService.generate_widget()
- Converts service response to domain entities
- Uses model_dump() for Pydantic serialization

**Reusability**: HIGH - Use case facade pattern

---

### generate_intelligent

**Purpose**: Generate intelligent UI with device context awareness

**Signature**:
```python
async def generate_intelligent(
    self, request: IntelligentGenerateRequest
) -> list[UIDescriptor]:
```

**Lines**: 37-63

**Key Code**:
```python
async def generate_intelligent(
    self, request: IntelligentGenerateRequest
) -> list[UIDescriptor]:
    """Generate intelligent UI with device context awareness.

    Returns domain entities (UIDescriptor).
    """
    from services.widget_spawner.intelligent_agent import IntelligentUIGenerator

    generator = IntelligentUIGenerator()
    result = generator(
        user_query=request.prompt, device_context=request.device_context
    )

    # Convert service response to domain entities
    return [
        UIDescriptor(
            id=w.get("id", ""),
            type=w.get("type", "markdown"),
            timestamp=w.get("timestamp", ""),
            title=w.get("title"),
            content=w.get("content"),
            dismissible=w.get("dismissible", True),
            metadata=w.get("metadata", {}),
        )
        for w in result.widgets
    ]
```

**What Works**:
- ✅ Device context awareness
- ✅ Returns domain entities
- ✅ Safe extraction with .get() and defaults
- ✅ List comprehension

**Mistakes Found**:
- ⚠️ Manual dict unpacking instead of model_dump()
- **Inconsistency**: generate_widget() uses model_dump(), this uses .get()
- **Risk**: If service changes, this might break

**Behavioral Notes**:
- Uses IntelligentUIGenerator directly
- Converts dict response to UIDescriptor entities
- Defaults to "markdown" type if missing

**Reusability**: HIGH - Intelligent UI generation pattern

---

## Functions Extracted

### get_widget_generation_use_case

**Purpose**: Singleton getter for dependency injection

**Signature**:
```python
def get_widget_generation_use_case() -> WidgetGenerationUseCase:
```

**Lines**: 70-75

**Key Code**:
```python
# Singleton getter for dependency injection
_widget_generation_use_case: WidgetGenerationUseCase | None = None


def get_widget_generation_use_case() -> WidgetGenerationUseCase:
    """Get singleton instance of WidgetGenerationUseCase."""
    global _widget_generation_use_case
    if _widget_generation_use_case is None:
        _widget_generation_use_case = WidgetGenerationUseCase()
    return _widget_generation_use_case
```

**What Works**:
- ✅ Singleton pattern
- ✅ Lazy initialization
- ✅ Global variable with type annotation
- ✅ Dependency injection friendly

**Mistakes Found**: None

**Reusability**: HIGH - Singleton getter pattern for DI

---

## File Summary

**Total Classes**: 1
**Total Functions**: 2 methods + 1 getter
**Lines of Code**: 76

**Violations**: None

**Success Patterns**:
- ✅ Use case facade pattern
- ✅ Returns domain entities, not DTOs
- ✅ Singleton getter for dependency injection
- ✅ Lazy imports (from inside functions)
- ✅ Async methods for I/O operations
- ✅ Device context awareness

**Overall Assessment**: EXCELLENT - Clean Architecture use case layer.

**Key Learnings for Real AgentX**:
1. ✅ **Use Case Facades**: Wrap services with use case classes
2. ✅ **Return Domain Entities**: Use cases return entities, not DTOs
3. ✅ **Singleton Getters**: Use global + getter for DI
4. ✅ **Lazy Imports**: Import services inside functions
5. ⚠️ **Consistent Conversion**: Use same pattern (model_dump vs .get)

**Reuse for Real AgentX**: ✅ REQUIRED - Use this use case pattern.

---

## Architectural Note

**Clean Architecture Layering**:
- Domain Entity: `UIDescriptor` (innermost layer)
- Use Case: `WidgetGenerationUseCase` (application layer)
- Service: `WidgetSpawnerService` (infrastructure layer)

The use case acts as a facade, hiding service complexity from the API layer.

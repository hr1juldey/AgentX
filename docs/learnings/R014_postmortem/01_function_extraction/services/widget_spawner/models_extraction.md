# models.py - Function Extraction

## File: services/widget_spawner/models.py

### Primary Purpose
Pydantic models for widget generation (DEPRECATED - now imports from domain layer).

### Key Classes

#### `WidgetDescriptor` (DEPRECATED)
**Status**: ⚠️ DEPRECATED - Import from `domain.entities.ui_descriptor.UIDescriptor`

**Current implementation**: Just an alias to UIDescriptor for backward compatibility.

```python
WidgetDescriptor = UIDescriptor
```

---

#### `WidgetGenerationRequest(BaseModel)`
**Purpose**: Request for widget generation.

**Fields**:
- `prompt`: str - User's prompt
- `widget_type`: str | None - Optional specific widget type

---

#### `MultiWidgetGenerationResponse(BaseModel)`
**Purpose**: Response from multi-widget generation using ReAct agent.

**Fields**:
- `widgets`: list[UIDescriptor] - Generated widgets
- `tools_used`: list[str] | None - Tools used by ReAct
- `reasoning`: str | None - ReAct reasoning trace
- `preview_data`: dict[str, Any] | None - Preview data for UI

---

### Legacy Aliases

**For backward compatibility**:
- `WidgetGenerationResponse = MultiWidgetGenerationResponse`
- `WidgetResponse = MultiWidgetGenerationResponse`

---

### Architectural Patterns

1. **Migration pattern**: Old models redirect to new domain layer
2. **Backward compatibility**: Keep old names working
3. **Clean separation**: Domain entities separate from service models

---

### Dependencies

**Internal**:
- `domain.entities.ui_descriptor.UIDescriptor`: New canonical location

**External**:
- `pydantic`: BaseModel
- `typing`: Type hints

---

### Lessons Learned

1. **Migrate to domain layer**: Service models should redirect to domain entities
2. **Keep backward compatibility**: Old imports still work via aliases
3. **Mark deprecation clearly**: Use ⚠️ warnings in docstrings
4. **Clean Architecture**: Domain entities are the single source of truth

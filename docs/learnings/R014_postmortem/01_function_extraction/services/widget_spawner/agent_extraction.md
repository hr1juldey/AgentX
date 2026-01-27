# agent.py - Function Extraction

## File: services/widget_spawner/agent.py

### Primary Purpose
Module init file that exports widget spawner agents.

### Exports

**Classes**:
- `MultiWidgetSpawnerAgent`: ReAct agent for spawning multiple widgets
- `SingleWidgetSpawnerAgent`: Fallback agent for single widget generation

**Usage**:
```python
from services.widget_spawner.agent import (
    MultiWidgetSpawnerAgent,
    SingleWidgetSpawnerAgent
)
```

---

### Architectural Patterns

1. **Module facade**: Exports public API from internal modules
2. **Backward compatibility**: Supports both multi and single widget generation

---

### Dependencies

**Internal**:
- `services.widget_spawner.multi_widget_agent`: MultiWidgetSpawnerAgent
- `services.widget_spawner.single_widget_agent`: SingleWidgetSpawnerAgent

---

### Lessons Learned

1. **Module init files as facades**: Clean API surface for consumers
2. **Export both agents**: Multi-widget for complex queries, single for simple

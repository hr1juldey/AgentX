# layout_utils.py - Function Extraction

## File: services/widget_spawner/layout_utils.py

### Primary Purpose
Generate x, y positions for widgets based on layout type and device context.

### Key Functions

#### `generate_positions(plan: Dict[str, Any], device_context: Dict[str, Any]) -> Dict[str, Any]`
**Purpose**: Generate suggested x, y positions for widgets.

**Parameters**:
- `plan`: Presentation plan with layout type and widgets
- `device_context`: Device info (type, screen_width, screen_height)

**Layout types**:
- `"simple_vertical"`: generate_vertical_layout()
- `"grid_2column"`: generate_grid_2column_layout()
- `"grid_3column"`: generate_grid_3column_layout()
- `"masonry"`: generate_masonry_layout()
- Other: generate_default_layout()

**Returns**: Updated plan with x, y positions added to widgets.

**Key insight**: Frontend can use these positions OR override with its own layout.

---

### Architectural Patterns

1. **Layout strategy pattern**: Different layout functions for different types
2. **Device-aware**: Uses screen dimensions from device_context
3. **Optional positioning**: Frontend can override backend suggestions

---

### Dependencies

**Internal**:
- `services.widget_spawner.layouts`: generate_*_layout functions

**External**:
- `logging`: Standard logging
- `typing`: Type hints

---

### Lessons Learned

1. **Backend suggestions are optional**: Frontend has final say on layout
2. **Layout types matter**: Different content needs different layouts
3. **Device context is critical**: Mobile needs different positions than desktop
4. **Strategy pattern**: Layout functions are swappable

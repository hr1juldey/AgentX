# vertical.py - Function Extraction

## File: services/widget_spawner/layouts/vertical.py

### Primary Purpose
Vertical stacking layout for widgets - simple one-column layout.

### Key Functions

#### `generate_vertical_layout(widgets: List[Dict], screen_width: int, screen_height: int) -> List[Dict]`
**Purpose**: Stack widgets vertically with spacing.

**Constants**:
- `y_offset`: Starts at 100
- `widget_height`: 350 pixels
- Spacing: 50 pixels between widgets

**Positioning**:
- `x`: `screen_width // 2 - 250` (centered, 500px wide)
- `y`: Increments by widget_height + spacing for each widget

**Returns**: List of widgets with x, y positions added.

---

### Architectural Patterns

1. **Simple vertical stack**: Widgets arranged in single column
2. **Centered positioning**: Horizontal center based on screen width
3. **Fixed spacing**: Consistent 50px gap between widgets

---

### Dependencies

**Internal**:
- None (standalone layout)

**External**:
- `typing`: Type hints

---

### Lessons Learned

1. **Vertical stack is simplest**: One column, centered
2. **Fixed heights work**: 350px height for all widgets
3. **Spacing matters**: 50px gap prevents visual crowding
4. **Center alignment**: x = screen_width // 2 - widget_width // 2

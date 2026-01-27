# masonry.py - Function Extraction

## File: services/widget_spawner/layouts/masonry.py

### Primary Purpose
Masonry-style layout with varying heights for widgets - Pinterest-style layout.

### Key Functions

#### `generate_masonry_layout(widgets: List[Dict], screen_width: int, screen_height: int) -> List[Dict]`
**Purpose**: Masonry-style layout with varying heights.

**Logic**:
1. Track column heights for 3 columns (start at 100)
2. For each widget:
   - Find shortest column using `min(range(3), key=lambda c: column_heights[c])`
   - Determine widget height based on type:
     - chart: 300px
     - markdown: 200px
     - other: 150px
   - Position widget at shortest column
   - Update column height

**Returns**: List of widgets with x, y positions added.

**Key insight**: Widgets flow to shortest column, balancing layout.

---

#### `generate_default_layout(widgets: List[Dict], screen_width: int, screen_height: int) -> List[Dict]`
**Purpose**: Fallback layout - centered stack.

**Implementation**: Delegates to `generate_vertical_layout()`.

**Use case**: Unknown layout types fall back to vertical.

---

### Architectural Patterns

1. **Shortest-column strategy**: Balance layout by placing in shortest column
2. **Type-based heights**: Different widget types have different heights
3. **Column height tracking**: Maintain running total for each column
4. **Fallback pattern**: Unknown layouts use vertical stack

---

### Dependencies

**Internal**:
- `services.widget_spawner.layouts.vertical`: generate_vertical_layout (for fallback)

**External**:
- `typing`: Type hints

---

### Lessons Learned

1. **Shortest column prevents gaps**: Always fill shortest column first
2. **Type-based heights vary**: Charts are taller than cards
3. **Column height tracking**: Need persistent state across all widgets
4. **Fallback is important**: Unknown layout types shouldn't crash
5. **Masonry looks organic**: Varying heights create visual interest

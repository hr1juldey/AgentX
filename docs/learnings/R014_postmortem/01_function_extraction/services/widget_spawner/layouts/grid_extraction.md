# grid.py - Function Extraction

## File: services/widget_spawner/layouts/grid.py

### Primary Purpose
2-column and 3-column grid layouts for widgets.

### Key Functions

#### `generate_grid_2column_layout(widgets: List[Dict], screen_width: int, screen_height: int) -> List[Dict]`
**Purpose**: Two column grid layout.

**Constants**:
- `y_offset`: Starts at 100
- `widget_height`: 300 pixels
- Left column x: 100
- Right column x: `screen_width // 2 + 50`

**Logic**:
- Alternate between left and right columns
- Increment y_offset after placing right column widget
- Reset to left column after each pair

**Returns**: List of widgets with x, y positions added.

---

#### `generate_grid_3column_layout(widgets: List[Dict], screen_width: int, screen_height: int) -> List[Dict]`
**Purpose**: Three column grid layout.

**Constants**:
- `y_offset`: Starts at 100
- `widget_height`: 250 pixels
- `column_width`: `screen_width // 3`

**Logic**:
- Distribute widgets across 3 columns
- x position: `(column * column_width) + 50`
- Increment y_offset after completing a row (3 widgets)
- Reset column counter after 3 widgets

**Returns**: List of widgets with x, y positions added.

---

### Architectural Patterns

1. **Grid layout**: Fixed number of columns (2 or 3)
2. **Row-based positioning**: Fill rows left-to-right
3. **Column width calculation**: Distribute screen width evenly

---

### Dependencies

**Internal**:
- None (standalone layouts)

**External**:
- `typing`: Type hints

---

### Lessons Learned

1. **Grid layouts need row logic**: Increment y after completing a row
2. **Column width divides screen**: screen_width // num_columns
3. **Alternating pattern**: Left/right toggle for 2-column
4. **Column counter**: Track current column (0, 1, 2) for 3-column

# sequencer_utils.py - Function Extraction

## File: services/pipeline/sequencer_utils.py

### Primary Purpose
Helper functions for SEQUENCER delivery plan creation.

### Key Functions

#### `create_delivery_plan(sequence: List[Dict[str, Any]], visual_hierarchy: List[str]) -> List[Dict[str, Any]]`
**Purpose**: Create detailed delivery plan from sequence.

**Parameters**:
- `sequence`: List with widget, order, delay_sec
- `visual_hierarchy`: List of visual roles (hero, insights, details)

**Logic**:
1. Iterate through sequence items
2. Determine visual_role based on order and hierarchy (modulo logic)
3. Set delivery_type based on delay (0 = immediate, >0 = staggered)

**Returns**: Delivery plan with widget, order, delay_sec, visual_role, delivery_type.

**Key insight**: Maps sequence items to visual hierarchy positions.

---

### Architectural Patterns

1. **Mapping**: Maps sequence items to visual roles
2. **Delivery classification**: Immediate vs staggered based on delay
3. **Modulo positioning**: `role_index = min(order - 1, len(visual_hierarchy) - 1)`

---

### Dependencies

**Internal**:
- None (standalone utilities)

---

### Lessons Learned

1. **Delivery plans need visual roles**: Tells frontend how to display each widget
2. **Immediate vs staggered**: Zero delay = immediate, positive delay = staggered
3. **Modulo for positioning**: Maps order to hierarchy position without overflow

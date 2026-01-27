# Function Postmortem: services/master_agent/delivery/planning.py

## Metadata
- **File**: services/master_agent/delivery/planning.py
- **Lines of Code**: 114
- **Purpose**: Widget ordering and delay calculation for staggered delivery
- **Dependencies**: None (pure logic)

---

## Analysis

**File Status**: PRODUCTION DSPy MODULE

**Purpose**: Implements "consultant-style" widget delivery with strategic timing. Priority widgets (markdown, search-results) get immediate delivery, others are spaced 2-5 seconds apart for natural conversation flow.

---

## Classes Extracted

### `DeliveryPlanning`

**Purpose**: Handles widget ordering and delay calculation for delivery.

**Constants**:
- `DEFAULT_MIN_DELAY = 2.0` - Minimum seconds between widgets
- `DEFAULT_MAX_DELAY = 5.0` - Maximum seconds between widgets
- `PRIORITY_WIDGETS = ["markdown", "search-result"]` - Widgets that get fast delivery

**Constructor Parameters**:
- `min_delay: float = DEFAULT_MIN_DELAY` - Minimum delay between widgets
- `max_delay: float = DEFAULT_MAX_DELAY` - Maximum delay between widgets

**Design Philosophy**: 2-5 second spacing mimics human consultant behavior (not instantaneous, not too slow)

---

#### `order_widgets_by_sequence(widgets: list, sequence: list) -> list`
Orders widgets according to the planned sequence from Sequencer agent.

**Parameters**:
- `widgets: list` - List of widget descriptors (dicts or objects)
- `sequence: list` - Ordered list from Sequencer agent

**Returns**: `list` - Ordered list of widgets

**Algorithm**:
1. Iterate through sequence items
2. For each sequence item, find matching widget by type
3. Add matched widget to ordered list (if not already added)
4. Add any remaining widgets not in sequence

**Type Handling**:
```python
# Handle both dict and object widgets
if isinstance(w, dict):
    w_type = w.get("descriptor_type") or w.get("type")
elif hasattr(w, "descriptor_type"):
    w_type = w.descriptor_type
elif hasattr(w, "type"):
    w_type = w.type
```

**Fallback Behavior**: Widgets not in sequence are appended at end (preserves all widgets)

**Pattern**: Flexible type checking (dict vs object) for backward compatibility

---

#### `calculate_delays(widgets: list) -> list[float]`
**Main Function**: Calculates delivery delays with priority handling.

**Parameters**:
- `widgets: list` - List of widgets to calculate delays for

**Returns**: `list[float]` - List of delay values for each widget (accumulated)

**Priority Strategy**:
1. **First widget**: `0.0` delay (immediate delivery)
2. **Priority widgets** (markdown, search-result): `min_delay / 2` (fast delivery)
3. **Other widgets**: Linear interpolation between min and max delay

**Delay Formula**:
```python
delay = min_delay + ((max_delay - min_delay) * (i / max(len(widgets) - 1, 1)))
```

**Accumulation**: Delays are cumulative (each widget waits from start, not from previous)

**Example Calculation** (5 widgets, min=2.0, max=5.0):
```
Widget 0: 0.0s (immediate)
Widget 1: 1.0s (priority, min/2)
Widget 2: 3.5s (2 + (5-2) * (2/4))
Widget 3: 5.75s (2 + (5-2) * (3/4))
Widget 4: 8.5s (2 + (5-2) * (4/4))
```

**Type Handling**: Same flexible type checking as `order_widgets_by_sequence`

**Key Design Decisions**:
1. **Accumulated delays**: Each delay is from start, not from previous (simpler scheduling)
2. **Priority fast-tracking**: Markdown/search-results get delivered sooner
3. **Linear spacing**: Prevents clustering, creates even distribution
4. **First widget immediate**: User sees something immediately

---

## File Summary

**Total Classes**: 1
**Lines of Code**: 114

**Overall Assessment**: Clean implementation of consultant-style delivery timing. Good UX pattern for natural conversation flow.

**Key Learnings for Real AgentX**:
1. ✅ **Consultant-style delivery**: 2-5 second spacing mimics human behavior
2. ✅ **Priority widgets**: Important content (markdown, search) gets fast delivery
3. ✅ **Accumulated delays**: Each delay from start, not from previous (easier scheduling)
4. ✅ **Flexible type handling**: Supports both dict and object widgets
5. ✅ **Linear interpolation**: Prevents clustering, creates even distribution
6. ✅ **Immediate first widget**: Reduces perceived latency

**Reuse for Real AgentX**: ✅ **HIGH PRIORITY**
- Use for any "progressive disclosure" UI pattern
- Apply to:
  - Multi-step responses
  - Streaming data presentation
  - Progressive loading of complex dashboards
- Adjust timing based on content type:
  - Text: 2-3 seconds
  - Charts: 3-5 seconds (needs time to absorb)
  - Cards: 1-2 seconds (quick to read)

**Potential Improvements**:
- Add widget-specific timing (charts slower than text)
- Add user preference control (fast vs slow delivery)
- Add "skip wait" button for impatient users
- Consider content length (longer markdown = longer delay)
- Add dynamic timing based on engagement (if user scrolls, deliver faster)

**UX Pattern**: This is a "progressive disclosure" pattern - reveal information gradually to avoid overwhelming the user

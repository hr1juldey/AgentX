# delivery_planner.py - Function Extraction

## File: `services/master_agent/delivery_planner.py`

## Purpose
Staggered delivery logic for consultant-style widget presentation. Plans and executes delayed widget delivery.

---

## Classes

### `DeliveryPlan` (dataclass)
**Purpose**: Plan for delivering widgets with staggered timing.

**Fields**:
- `widgets` (list): List of UIDescriptor widgets
- `delays` (list[float]): Delay in seconds for each widget
- `total_duration` (float): Total time for all deliveries

**Methods**:
- `get_delivery_schedule() -> list[tuple[float, dict]]`: Get delivery schedule as (delay, widget) tuples

**Behavior**:
- Zips delays with widgets
- Converts widgets to dict if they have model_dump() method (Pydantic models)
- Returns list of tuples ready for async execution

**Mistakes/Issues**:
- **model_dump() check**: Handles both Pydantic models and plain dicts - good defensive programming

**Usage Notes**:
- Used by DeliveryExecution.deliver_with_delay()
- Each tuple: (delay_seconds, widget_as_dict)

---

### `DeliveryPlanner`
**Purpose**: Plans staggered widget delivery with consultant-style pacing (2-5 seconds between widgets).

**Constructor Parameters**:
- `min_delay` (float): Minimum delay between widgets (default: 2.0)
- `max_delay` (float): Maximum delay between widgets (default: 5.0)

**Composition Pattern**:
- Contains `DeliveryPlanning` instance (logic)
- Contains `DeliveryExecution` instance (async execution)

**Methods**:
- `plan_delivery(widgets, sequence) -> DeliveryPlan`: Create delivery plan with staggered timing
- `deliver_with_delay(delivery_plan, delivery_callback) -> None`: Execute staggered delivery with async delays

---

## Functions (from delivery/ subdirectory)

### `DeliveryPlanning.order_widgets_by_sequence(widgets, sequence) -> list`
**Purpose**: Order widgets according to the planned sequence.

**Parameters**:
- `widgets` (list): List of widget descriptors
- `sequence` (list): Ordered list from Sequencer agent

**Returns**:
- `list`: Ordered list of widgets

**Behavior**:
1. Iterates through sequence items
2. For each sequence item, finds matching widget by type
3. Adds matching widget to ordered list (if not already added)
4. Adds remaining widgets not in sequence
5. Returns ordered list

**Mistakes/Issues**:
- **Handles both dict and object widgets**: Checks descriptor_type, type attribute
- **No duplicates**: Checks if widget already in ordered list
- **Preserves all widgets**: Doesn't lose widgets not in sequence

**Usage Notes**:
- Sequence from Sequencer determines widget order
- Widgets can be dicts or objects with type/descriptor_type attributes

---

### `DeliveryPlanning.calculate_delays(widgets) -> list[float]`
**Purpose**: Calculate delivery delays with priority handling.

**Parameters**:
- `widgets` (list): List of widgets to calculate delays for

**Returns**:
- `list[float]`: List of delay values for each widget

**Behavior**:
- Priority widgets (markdown, search-result) get minimal delay
- First widget: 0.0 seconds (immediate)
- Priority widgets: min_delay / 2 (1.0 second)
- Other widgets: Spread between min_delay and max_delay based on position
- Accumulates delays for each widget (staggered delivery)

**Example** (5 widgets, min=2.0, max=5.0):
- Widget 0: 0.0s (immediate)
- Widget 1 (markdown): 1.0s (priority, min/2)
- Widget 2: 3.5s (2.0 + 3.0 * 1/4)
- Widget 3: 5.5s (2.0 + 3.0 * 2/4)
- Widget 4: 8.0s (2.0 + 3.0 * 3/4)

**Mistakes/Issues**:
- **Fixed delays**: Doesn't adapt to widget complexity
- **Linear progression**: Delays spread evenly, not based on content

**Usage Notes**:
- Consultant-style pacing: don't overwhelm user
- Priority widgets delivered first/quickly

---

### `DeliveryExecution.deliver_with_delay(delivery_plan, delivery_callback) -> None`
**Purpose**: Execute staggered delivery with async delays.

**Parameters**:
- `delivery_plan` (DeliveryPlan): The planned delivery schedule
- `delivery_callback` (Callable): Async function to call for each widget delivery

**Returns**: None (async)

**Behavior**:
1. Gets delivery schedule from plan
2. Creates async task for each widget delivery with its delay
3. Waits for all deliveries to complete
4. Each task: await sleep(delay) → await callback(widget)

**Mistakes/Issues**:
- **Async pattern**: Requires callback to be async function
- **Parallel execution**: All deliveries scheduled simultaneously, not sequential

**Usage Notes**:
- Callback signature: `async def callback(widget: dict) -> None`
- Typically sends widget to frontend via WebSocket
- Uses asyncio.gather() to wait for all deliveries

---

## Patterns and Lessons

### Staggered Delivery Pattern
**Goal**: Consultant-style presentation - don't overwhelm user with all widgets at once.

**Implementation**:
1. Order widgets by sequence (from Sequencer)
2. Calculate delays based on:
   - Position (first widget = immediate)
   - Widget type (priority widgets = faster)
   - Total count (spread delays evenly)
3. Execute with asyncio.sleep() delays

### Priority Widgets
```python
PRIORITY_WIDGETS = ["markdown", "search-result"]
```
- Markdown and search-result get delivered first (or quickly)
- Other widgets spaced 2-5 seconds apart

### Delay Calculation Logic
```python
# First widget: immediate
delay = 0.0

# Priority widgets: half min_delay
delay = min_delay / 2  # 1.0 second

# Other widgets: spread between min and max
delay = min_delay + ((max_delay - min_delay) * (i / (count - 1)))
```

**Accumulated delays**:
- Each delay is added to previous (staggered)
- Widget 3 arrives at delay[0] + delay[1] + delay[2] + delay[3]
- Creates natural "trickle" effect

### Composition Pattern
```python
class DeliveryPlanner:
    def __init__(self):
        self._planning = DeliveryPlanning()  # Logic
        self._execution = DeliveryExecution()  # Async execution
```

**Why?**
- Separates planning from execution
- Planning can be tested without async
- Execution can be tested with mock plans

### Widget Ordering Logic
```python
def order_widgets_by_sequence(widgets, sequence):
    ordered = []
    for seq_item in sequence:
        widget_type = seq_item.get("widget", "")
        for w in widgets:
            if w.type == widget_type and w not in ordered:
                ordered.append(w)
    # Add remaining widgets not in sequence
    for w in widgets:
        if w not in ordered:
            ordered.append(w)
```

**Key Points**:
- Handles both dict and object widgets
- Preserves sequence order
- Doesn't lose widgets not in sequence
- No duplicates in output

---

## What Works
- **Staggered delivery**: Good UX for complex results
- **Priority handling**: Key widgets delivered first
- **Flexible timing**: Configurable min/max delays
- **Composition**: Planning separated from execution
- **Defensive programming**: Handles both dicts and objects

### What Doesn't Work
- **Fixed delays**: Doesn't adapt to widget complexity
- **No user control**: Can't skip ahead or pause
- **No feedback**: User doesn't know how many widgets coming
- **Parallel scheduling**: All tasks created at once (not sequential)

---

## Dependencies
- `dataclasses` - dataclass
- `services.master_agent.delivery` - DeliveryExecution, DeliveryPlanning

## Used By
- `agent_setup.py` - Initialize DeliveryPlanner
- `execution.py` - PipelineExecution uses DeliveryPlanner
- `factory/streaming.py` - StreamingExecution uses DeliveryPlanner

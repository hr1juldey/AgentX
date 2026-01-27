# simple_widgets.py - Function Extraction

## File: services/widget_spawner/builders/simple_widgets.py

### Primary Purpose
Helper functions for building simple widget data (no DSPy results) - static widgets.

### Key Functions

#### `build_action_widget(user_query: str, widget_id: str) -> dict`
**Purpose**: Build action widget data.

**Fields**:
- `id`: widget_id
- `type`: "action"
- `title`: "Quick Action"
- `content`: "Action requested: {user_query}"
- `metadata`: {"button_text": DEFAULT_ACTION_BUTTON_TEXT, "action_id": DEFAULT_ACTION_ID}
- `timestamp`: Current UTC datetime
- `dismissible`: True

---

#### `build_confirmation_widget(user_query: str, widget_id: str) -> dict`
**Purpose**: Build confirmation widget data.

**Fields**:
- `id`: widget_id
- `type`: "confirmation"
- `title`: "Confirm Action"
- `content`: None
- `metadata`: {"message": "Please confirm: {user_query}", "confirm_label": DEFAULT_CONFIRM_LABEL, "cancel_label": DEFAULT_CANCEL_LABEL}
- `timestamp`: Current UTC datetime
- `dismissible`: True

---

### Architectural Patterns

1. **Static widgets**: No DSPy/LLM needed - purely template-based
2. **User query in content**: Echo user's request back to them
3. **Configurable defaults**: Button text and labels from config

---

### Dependencies

**Internal**:
- `services.widget_spawner.config`: DEFAULT_ACTION_* and DEFAULT_CONFIRM_* constants

**External**:
- `datetime`: Timestamp generation
- `typing`: Type hints

---

### Lessons Learned

1. **Not all widgets need LLM**: Action/confirmation are static templates
2. **Echo user query**: Helps user understand what they requested
3. **Defaults are configurable**: Button text can be changed via config
4. **Simple builders are fast**: No LLM calls = instant widget generation

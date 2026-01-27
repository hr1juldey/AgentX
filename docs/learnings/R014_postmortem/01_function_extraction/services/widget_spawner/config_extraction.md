# config.py - Function Extraction

## File: services/widget_spawner/config.py

### Primary Purpose
Constants and configuration for widget generation.

### Key Constants

#### Widget Types
- `AVAILABLE_WIDGET_TYPES`: List of 9 widget types (markdown, card, form, progress, action, confirmation, image, gallery, chart)

#### Default Widget Configurations
- `DEFAULT_CARD_ACTIONS`: `[{"label": "Learn More", "action": "learn_more"}, ...]`
- `DEFAULT_FORM_FIELDS`: 3 fields (name, email, feedback)
- `DEFAULT_FORM_SUBMIT_LABEL`: "Submit"
- `DEFAULT_FORM_TITLE`: "User Input Form"
- `DEFAULT_CHART_DATA`: 6 months of data (month, value, target)
- `DEFAULT_CHART_DATA_KEYS`: `["value", "target"]`

#### Image/URL Constants
- `DEFAULT_IMAGE_BASE_URL`: `"https://picsum.photos"`
- `DEFAULT_IMAGE_WIDTH`: 800
- `DEFAULT_IMAGE_HEIGHT`: 600
- `DEFAULT_GALLERY_IMAGE_WIDTH`: 400
- `DEFAULT_GALLERY_IMAGE_HEIGHT`: 400

#### Widget-Specific Defaults
- `DEFAULT_ACTION_BUTTON_TEXT`: "Execute Action"
- `DEFAULT_ACTION_ID`: "quick_action"
- `DEFAULT_CONFIRM_LABEL`: "Confirm"
- `DEFAULT_CANCEL_LABEL`: "Cancel"
- `DEFAULT_PROGRESS_VALUE_DIVISOR`: 100

#### Agent Configuration
- `DEFAULT_MAX_ITERS`: 5
- `DEFAULT_OLLAMA_BASE_URL`: `"http://localhost:11434"`
- `DEFAULT_MODEL`: `"gemma3:4b"`

---

### Architectural Patterns

1. **Constants module**: Centralized configuration
2. **Final types**: Uses `Final` for immutable constants
3. **Default values**: Provides fallbacks for all widget types

---

### Dependencies

**Internal**:
- None (configuration only)

**External**:
- `typing.Final`: Type hint for constants

---

### Lessons Learned

1. **Centralize defaults**: Single source of truth for widget configurations
2. **Use Final type**: Marks constants as immutable
3. **Provide defaults**: All widget types have sensible fallbacks
4. **URL constants**: Image sources have configurable dimensions

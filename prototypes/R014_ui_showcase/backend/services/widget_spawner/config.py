# =============================================================================
# AGENTX Widget Spawner Configuration
# =============================================================================
# Constants and configuration for widget generation
# =============================================================================

from typing import Final

# =============================================================================
# Widget Type Constants
# =============================================================================

AVAILABLE_WIDGET_TYPES: Final = [
    "markdown",
    "card",
    "form",
    "progress",
    "action",
    "confirmation",
    "image",
    "gallery",
    "chart",
]

# =============================================================================
# Default Widget Configurations
# =============================================================================

# Default card actions
DEFAULT_CARD_ACTIONS: Final = [
    {"label": "Learn More", "action": "learn_more"},
    {"label": "Share", "action": "share"},
]

# Default form fields
DEFAULT_FORM_FIELDS: Final = [
    {"name": "name", "type": "text", "label": "Your Name", "required": True},
    {"name": "email", "type": "email", "label": "Email Address", "required": True},
    {
        "name": "feedback",
        "type": "textarea",
        "label": "Your Feedback",
        "required": True,
    },
]

# Default form labels
DEFAULT_FORM_SUBMIT_LABEL: Final = "Submit"
DEFAULT_FORM_TITLE: Final = "User Input Form"

# Default chart data
DEFAULT_CHART_DATA: Final = [
    {"month": "Jan", "value": 400, "target": 300},
    {"month": "Feb", "value": 300, "target": 350},
    {"month": "Mar", "value": 600, "target": 400},
    {"month": "Apr", "value": 800, "target": 500},
    {"month": "May", "value": 500, "target": 600},
    {"month": "Jun", "value": 700, "target": 650},
]

# Default chart keys
DEFAULT_CHART_DATA_KEYS: Final = ["value", "target"]

# =============================================================================
# Image/URL Constants
# =============================================================================

DEFAULT_IMAGE_BASE_URL: Final = "https://picsum.photos"
DEFAULT_IMAGE_WIDTH: Final = 800
DEFAULT_IMAGE_HEIGHT: Final = 600

DEFAULT_GALLERY_IMAGE_WIDTH: Final = 400
DEFAULT_GALLERY_IMAGE_HEIGHT: Final = 400

# =============================================================================
# Widget Type-specific Defaults
# =============================================================================

# Action widget defaults
DEFAULT_ACTION_BUTTON_TEXT: Final = "Execute Action"
DEFAULT_ACTION_ID: Final = "quick_action"

# Confirmation widget defaults
DEFAULT_CONFIRM_LABEL: Final = "Confirm"
DEFAULT_CANCEL_LABEL: Final = "Cancel"

# Progress widget defaults
DEFAULT_PROGRESS_VALUE_DIVISOR: Final = 100

# =============================================================================
# Agent Configuration
# =============================================================================

DEFAULT_MAX_ITERS: Final = 5
DEFAULT_OLLAMA_BASE_URL: Final = "http://localhost:11434"
DEFAULT_MODEL: Final = "gemma3:4b"

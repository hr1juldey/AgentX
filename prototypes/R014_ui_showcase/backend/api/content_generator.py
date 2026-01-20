# =============================================================================
# AGENTX R014 - Content Generator (Facade)
# =============================================================================
# Facade for accessing specialized widget generators
# =============================================================================

from api.generators import (
    InteractiveWidgetGenerator,
    MediaWidgetGenerator,
    TextWidgetGenerator,
)


class ContentGenerator:
    """Generate dynamic content for UI components using DSPy.

    This class acts as a facade, delegating to specialized generator classes.
    """

    # Text widgets
    generate_markdown = TextWidgetGenerator.generate_markdown
    generate_card = TextWidgetGenerator.generate_card
    generate_form = TextWidgetGenerator.generate_form

    # Interactive widgets
    generate_progress = InteractiveWidgetGenerator.generate_progress
    generate_action = InteractiveWidgetGenerator.generate_action
    generate_confirmation = InteractiveWidgetGenerator.generate_confirmation

    # Media widgets
    generate_image = MediaWidgetGenerator.generate_image
    generate_gallery = MediaWidgetGenerator.generate_gallery
    generate_chart = MediaWidgetGenerator.generate_chart

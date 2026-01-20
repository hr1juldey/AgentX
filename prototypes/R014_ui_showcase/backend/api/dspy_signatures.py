# =============================================================================
# AGENTX R014 - DSPy Signatures
# =============================================================================
# DSPy signatures for content generation
# =============================================================================

import dspy


class MarkdownContentSignature(dspy.Signature):
    """Generate markdown content."""

    topic = dspy.InputField(desc="Topic to write about")
    content = dspy.OutputField(desc="Markdown formatted content")


class CardContentSignature(dspy.Signature):
    """Generate card content."""

    topic = dspy.InputField(desc="Card topic")
    title = dspy.OutputField(desc="Card title")
    content = dspy.OutputField(desc="Card body content")


class WeatherCardSignature(dspy.Signature):
    """Generate weather card content."""

    location = dspy.InputField(desc="City name")
    weather_info = dspy.OutputField(desc="Weather description with emojis")


class SearchResultsSignature(dspy.Signature):
    """Generate search results."""

    query = dspy.InputField(desc="Search query")
    results = dspy.OutputField(desc="List of search results as numbered items")


class FormFieldsSignature(dspy.Signature):
    """Generate form fields description."""

    form_purpose = dspy.InputField(desc="What the form is for")
    fields_description = dspy.OutputField(desc="Form fields needed")


class FormContentSignature(dspy.Signature):
    """Generate full form content."""

    form_type = dspy.InputField(desc="Type of form (login, feedback, survey, etc.)")
    title = dspy.OutputField(desc="Form title")
    description = dspy.OutputField(desc="Form description")


class ProgressContentSignature(dspy.Signature):
    """Generate progress status."""

    task = dspy.InputField(desc="Task being performed")
    status_text = dspy.OutputField(desc="Current status message")


class ActionContentSignature(dspy.Signature):
    """Generate action button text."""

    action_type = dspy.InputField(desc="Type of action (approve, delete, submit, etc.)")
    button_text = dspy.OutputField(desc="Button label")
    description = dspy.OutputField(desc="Action description")


class ConfirmationContentSignature(dspy.Signature):
    """Generate confirmation dialog."""

    action = dspy.InputField(desc="Action to confirm")
    title = dspy.OutputField(desc="Dialog title")
    message = dspy.OutputField(desc="Confirmation message")


class ImageContentSignature(dspy.Signature):
    """Generate image widget content."""

    subject = dspy.InputField(desc="Image subject or theme")
    title = dspy.OutputField(desc="Image title")
    caption = dspy.OutputField(desc="Image caption or description")


class GalleryContentSignature(dspy.Signature):
    """Generate gallery widget content."""

    theme = dspy.InputField(desc="Gallery theme")
    title = dspy.OutputField(desc="Gallery title")
    description = dspy.OutputField(desc="Gallery description")


class ChartContentSignature(dspy.Signature):
    """Generate chart widget content."""

    data_topic = dspy.InputField(desc="Chart data topic")
    title = dspy.OutputField(desc="Chart title")
    description = dspy.OutputField(desc="Chart description")

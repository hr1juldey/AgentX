"""Markdown block descriptor for Real AgentX v0.1.

Specialized descriptor for markdown content blocks.
"""

from dataclasses import dataclass

from agentx.ui.descriptors.base import BaseUIDescriptor


@dataclass
class MarkdownBlockDescriptor(BaseUIDescriptor):
    """Markdown block descriptor.

    Renders markdown content with support for code blocks,
    lists, and other markdown features.
    """

    def __init__(self, content: str, code_block: bool = False):
        """Initialize markdown block descriptor.

        Args:
            content: Markdown content to render.
            code_block: Whether content is a code block.
        """
        super().__init__()
        self.component_type = self.component_type
        self.props = {
            "content": content,
            "code_block": code_block,
            "language": "text" if code_block else None,
        }

    def validate(self) -> bool:
        """Validate markdown block descriptor.

        Returns:
            bool: True if content is valid.
        """
        content = self.props.get("content", "")
        return isinstance(content, str) and len(content) > 0

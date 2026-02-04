"""TTS Formatter - Format agent response for natural speech synthesis."""

import logging
import re

logger = logging.getLogger(__name__)


# Patterns for markdown removal
_MARKDOWN_PATTERNS = [
    (r"\*\*(.+?)\*\*", r"\1"),  # Bold: **text** -> text
    (r"__(.+?)__", r"\1"),  # Bold: __text__ -> text
    (r"\*(.+?)\*", r"\1"),  # Italic: *text* -> text
    (r"_(.+?)_", r"\1"),  # Italic: _text_ -> text
    (r"```[\s\S]*?```", ""),  # Code blocks: remove entirely
    (r"`(.+?)`", r"\1"),  # Inline code: `code` -> code
    (r"#{1,6}\s*", ""),  # Headers: ## remove markers
    (r"\[([^\]]+)\]\([^)]+\)", r"\1"),  # Links: [text](url) -> text
]


def format_tts_phrase(agent_text: str) -> str:
    """Format agent response for natural speech synthesis.

    Adds punctuation, breaks long sentences, removes markdown.

    Args:
        agent_text: Raw agent response text

    Returns:
        Formatted text suitable for TTS synthesis
    """
    if not agent_text or len(agent_text.strip()) < 3:
        return agent_text

    text = agent_text.strip()

    # Remove markdown formatting
    text = _remove_markdown(text)

    # Ensure punctuation at end
    if text and text[-1] not in {".", "?", "!", "…", ";"}:
        text = text + "."

    # Break long sentences (30+ words)
    text = _break_long_sentences(text)

    # Add contractions for natural speech
    text = _add_conversational_contractions(text)

    # Clean up multiple spaces
    text = re.sub(r"\s+", " ", text).strip()

    logger.debug(f"TTS preprocessing: '{agent_text}' -> '{text}'")
    return text


def _remove_markdown(text: str) -> str:
    """Remove markdown formatting from text.

    Args:
        text: Text with markdown

    Returns:
        Plain text without markdown
    """
    for pattern, replacement in _MARKDOWN_PATTERNS:
        text = re.sub(pattern, replacement, text)

    # Clean up any leftover markdown artifacts
    text = re.sub(r"[#*_`{}\[\]]+", "", text)

    return text


def _break_long_sentences(text: str) -> str:
    """Break sentences longer than 30 words into shorter ones.

    Args:
        text: Text with potentially long sentences

    Returns:
        Text with shorter sentences
    """
    sentences = re.split(r"(?<=[.!?])\s+", text)
    result: list[str] = []

    for sentence in sentences:
        word_count = len(sentence.split())
        if word_count > 30:
            # Find natural break points (commas, conjunctions)
            parts = re.split(
                r"(,\s+|\s+(and|or|but|so|because)\s+)", sentence, maxsplit=1
            )
            if len(parts) > 1:
                # Insert break at first natural point
                break_idx = sentence.index(parts[1]) + len(parts[1])
                result.append(sentence[:break_idx].strip())  # type: ignore[list-item]
                result.append(sentence[break_idx:].strip())  # type: ignore[list-item]
            else:
                result.append(sentence)  # type: ignore[list-item]
        else:
            result.append(sentence)  # type: ignore[list-item]

    return " ".join(result)


def _add_conversational_contractions(text: str) -> str:
    """Add conversational contractions for natural speech.

    Args:
        text: Text to process

    Returns:
        Text with contractions
    """
    # Expand to contractions for natural speech
    contractions = {
        r"\bI am\b": "I'm",
        r"\byou are\b": "you're",
        r"\bwe are\b": "we're",
        r"\bthey are\b": "they're",
        r"\bthat is\b": "that's",
        r"\bit is\b": "it's",
        r"\bdo not\b": "don't",
        r"\bdoes not\b": "doesn't",
        r"\bdid not\b": "didn't",
        r"\bwill not\b": "won't",
        r"\bcannot\b": "can't",
    }

    for pattern, contraction in contractions.items():
        text = re.sub(pattern, contraction, text, flags=re.IGNORECASE)

    return text

"""STT Cleaner - Clean speech-to-text transcription output."""

import logging
import re

logger = logging.getLogger(__name__)


# Filler words to remove from STT output
_FILLER_WORDS = [
    r"\bum\b",
    r"\buh\b",
    r"\blike\b",
    r"\byou know\b",
    r"\ber\b",
    r"\bah\b",
]


def format_stt_query(stt_text: str) -> str:
    """Clean STT transcription output for agent input.

    Removes filler words and fixes basic grammar while preserving meaning.

    Args:
        stt_text: Raw STT transcription

    Returns:
        Cleaned text suitable for agent processing
    """
    if not stt_text or len(stt_text.strip()) < 3:
        return stt_text

    text = stt_text.strip()

    # Remove filler words (case-insensitive)
    for pattern in _FILLER_WORDS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # Clean up extra whitespace from filler removal
    text = re.sub(r"\s+", " ", text).strip()

    # Fix common ASR errors
    text = _fix_common_asr_errors(text)

    # Preserve proper by capitalizing first letter of sentences
    text = _capitalize_sentences(text)

    logger.debug(f"STT preprocessing: '{stt_text}' -> '{text}'")
    return text


def _fix_common_asr_errors(text: str) -> str:
    """Fix common ASR transcription errors.

    Args:
        text: Text with potential ASR errors

    Returns:
        Corrected text
    """
    # Common ASR error corrections
    corrections = {
        "whatcha": "what are you",
        "gonna": "going to",
        "wanna": "want to",
        "gotta": "got to",
        "kinda": "kind of",
        "sorta": "sort of",
    }

    for wrong, correct in corrections.items():
        text = re.sub(rf"\b{wrong}\b", correct, text, flags=re.IGNORECASE)

    return text


def _capitalize_sentences(text: str) -> str:
    """Capitalize first letter of sentences.

    Args:
        text: Text to capitalize

    Returns:
        Text with proper capitalization
    """
    # Capitalize first letter
    if text:
        text = text[0].upper() + text[1:]

    # Capitalize after sentence endings
    text = re.sub(r"([.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), text)

    return text

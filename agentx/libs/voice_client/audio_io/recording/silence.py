"""Silence detection and trimming utilities."""

import numpy as np


def trim_silence(
    audio: np.ndarray,
    threshold: float,
) -> np.ndarray:
    """Remove leading and trailing silence from audio.

    Args:
        audio: Audio array
        threshold: Silence threshold (RMS)

    Returns:
        Audio array with silence trimmed
    """
    # Find first non-silent sample
    start = 0
    for i in range(len(audio)):
        if abs(audio[i]) > threshold:
            start = i
            break
    else:
        # All silence
        return np.array([], dtype=audio.dtype)

    # Find last non-silent sample
    end = len(audio) - 1
    for i in range(len(audio) - 1, -1, -1):
        if abs(audio[i]) > threshold:
            end = i
            break

    return audio[start : end + 1]


def calculate_rms(audio: np.ndarray) -> float:
    """Calculate RMS (Root Mean Square) of audio.

    Args:
        audio: Audio array

    Returns:
        RMS value
    """
    return float(np.sqrt(np.mean(audio**2)))


def is_silent(audio: np.ndarray, threshold: float) -> bool:
    """Check if audio is below silence threshold.

    Args:
        audio: Audio array
        threshold: Silence threshold (RMS)

    Returns:
        True if audio is silent
    """
    return calculate_rms(audio) < threshold

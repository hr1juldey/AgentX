"""STT preprocessor node for the dynamic agent graph.

This node preprocesses STT (Speech-to-Text) input to determine
the input path and clean transcribed text.
"""

import re

from agentx.domain.models.graph_state import AgentState
from agentx.domain.models.stt_preprocessing import (
    InputPath,
    PreprocessedQuery,
)


def stt_preprocessor_node(state: AgentState) -> dict:
    """Preprocess STT input.

    Determines if input is TEXT or STT and preprocesses accordingly.
    For STT input, cleans transcription artifacts and validates.

    Args:
        state: Current agent state

    Returns:
        dict: Updated state with preprocessed_query and input_path
    """
    query = state["query"]
    input_path = state.get("input_path", InputPath.TEXT)

    # Detect input path if not set
    if input_path == InputPath.STT or _is_stt_input(query):
        input_path = InputPath.STT
        preprocessed = _preprocess_stt(query)
    else:
        input_path = InputPath.TEXT
        preprocessed = _preprocess_text(query)

    return {
        "input_path": input_path,
        "preprocessed_query": preprocessed.processed_query,
        "execution_path": ["stt_preprocessor"],
    }


def _is_stt_input(query: str) -> bool:
    """Detect if input is from STT.

    Checks for STT-specific patterns and artifacts.

    Args:
        query: Input query

    Returns:
        bool: True if STT input detected
    """
    stt_indicators = [
        "[laughter]",
        "[um]",
        "[ah]",
        "<noise>",
        "[pause]",
    ]

    query_lower = query.lower()
    return any(indicator in query_lower for indicator in stt_indicators)


def _preprocess_stt(query: str) -> PreprocessedQuery:
    """Preprocess STT input.

    Removes STT artifacts and normalizes text.

    Args:
        query: Raw STT input

    Returns:
        PreprocessedQuery: Preprocessed query
    """
    # Remove STT artifacts
    cleaned = query

    # Remove bracketed artifacts
    cleaned = re.sub(r"\[.*?\]", "", cleaned)

    # Remove filler words
    filler_words = ["um", "uh", "ah", "like", "you know"]
    for filler in filler_words:
        cleaned = re.sub(rf"\b{filler}\b", "", cleaned, flags=re.IGNORECASE)

    # Normalize whitespace
    cleaned = " ".join(cleaned.split())

    # Remove trailing punctuation
    cleaned = cleaned.strip().rstrip(".")

    return PreprocessedQuery(
        original_input=query,
        input_path=InputPath.STT,
        processed_query=cleaned,
        confidence=0.9,  # TODO: Get actual confidence from STT service
        metadata={"preprocessing": "stt"},
    )


def _preprocess_text(query: str) -> PreprocessedQuery:
    """Preprocess text input.

    Minimal preprocessing for text input.

    Args:
        query: Raw text input

    Returns:
        PreprocessedQuery: Preprocessed query
    """
    cleaned = query.strip()

    return PreprocessedQuery(
        original_input=query,
        input_path=InputPath.TEXT,
        processed_query=cleaned,
        confidence=1.0,
        metadata={"preprocessing": "text"},
    )


def route_by_input_path(state: AgentState) -> str:
    """Route based on detected input path.

    Args:
        state: Current agent state

    Returns:
        str: Routing path
    """
    input_path = state.get("input_path", InputPath.TEXT)

    if input_path == InputPath.STT:
        return "stt_preprocessor"
    else:
        return "query_planner"

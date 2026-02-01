"""Domain models for STT preprocessing.

This module defines the models for input path determination
and preprocessing of STT input.
"""

from enum import Enum

from pydantic import BaseModel, Field


class InputPath(str, Enum):
    """Input path for user query."""

    TEXT = "text"
    STT = "stt"


class PreprocessedQuery(BaseModel):
    """Result of preprocessing a query."""

    original_input: str = Field(description="Original user input")
    input_path: InputPath = Field(description="Detected input path")
    processed_query: str = Field(description="Preprocessed query text")
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in preprocessing result",
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Additional preprocessing metadata",
    )

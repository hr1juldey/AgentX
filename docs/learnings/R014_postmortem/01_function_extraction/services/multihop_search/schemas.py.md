# Function Extraction: services/multihop_search/schemas.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/multihop_search/schemas.py`

## File Size
79 lines

## Purpose

    cited_text: str = Field(..., description="Text cited from the source")
    document_index: int = Field(
        ..., description="Index of the document in search results"
    )
    document_title

## Key Classes
- `Citation`
- `HopEvent`
- `SearchRequest`
- `SearchResult`

## Key Functions
None

## Dependencies
- from __future__ import annotations
- from typing import Any
- from pydantic import BaseModel, Field

## Data Structures
See key classes above

## Business Logic
This module contains 4 classes and 0 functions.
It uses synchronous operations.
Code complexity: 59 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.534996
- Lines of code: 59

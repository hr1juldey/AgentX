# Function Extraction: application/dtos/responses.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/application/dtos/responses.py`

## File Size
38 lines

## Purpose

    status: str
    service: str
    llm: dict[str, str]


class SearchResultResponse(BaseModel):

## Key Classes
- `HealthResponse`
- `SearchResultResponse`

## Key Functions
None

## Dependencies
- from typing import Any
- from pydantic import BaseModel
- from domain.entities.ui_descriptor import UIDescriptor

## Data Structures
See key classes above

## Business Logic
This module contains 2 classes and 0 functions.
It uses synchronous operations.
Code complexity: 19 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.515880
- Lines of code: 19

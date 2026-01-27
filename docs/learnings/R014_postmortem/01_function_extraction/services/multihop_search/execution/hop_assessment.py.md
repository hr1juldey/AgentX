# Function Extraction: services/multihop_search/execution/hop_assessment.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/multihop_search/execution/hop_assessment.py`

## File Size
102 lines

## Purpose

    SRP: Assess completeness and determine if stopping is appropriate.

## Key Classes
- `HopAssessment`

## Key Functions
- async `assess()`
- `__init__()`
- `get_gap_description()`
- `get_confidence()`

## Dependencies
- from __future__ import annotations
- import logging
- from typing import TYPE_CHECKING
- import dspy
- from services.multihop_search.execution.hop_helpers import summarize_documents
- from services.multihop_search.search_client import SearchResultItem
- from services.multihop_search.reflection import CompletenessAssessor

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 4 functions.
It focuses on async operations.
Code complexity: 70 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.532359
- Lines of code: 70

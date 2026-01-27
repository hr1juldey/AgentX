# Function Extraction: services/tools/researcher/content_filter.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/tools/researcher/content_filter.py`

## File Size
134 lines

## Purpose

    Input: A chunk of web page content (max 2000 chars) + research goal
    Output: Only the relevant sentences/paragraphs that help answer the goal

    Examples:
        Input chunk: "The company w

## Key Classes
- `FilterRelevantContent`
- `ExtractRelevantLinks`
- `ContentFilterModule`

## Key Functions
- `__init__()`
- `filter_content()`
- `extract_links()`

## Dependencies
- import dspy
- from services.tools.researcher.link_parser import parse_relevant_links

## Data Structures
See key classes above

## Business Logic
This module contains 3 classes and 3 functions.
It uses synchronous operations.
Code complexity: 91 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.555163
- Lines of code: 91

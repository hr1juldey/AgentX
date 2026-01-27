# Function Extraction: services/tools/contextualizer/signatures.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/tools/contextualizer/signatures.py`

## File Size
48 lines

## Purpose

    query: str = dspy.InputField(desc="User query")
    result: str = dspy.InputField(desc="Search result to score")
    relevance_score: float = dspy.OutputField(desc="Relevance score from 0.0 to 1.

## Key Classes
- `ScoreRelevanceSignature`
- `CheckRelevanceSignature`
- `ShouldIncludeSignature`

## Key Functions
None

## Dependencies
- import dspy

## Data Structures
See key classes above

## Business Logic
This module contains 3 classes and 0 functions.
It uses synchronous operations.
Code complexity: 27 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.548389
- Lines of code: 27

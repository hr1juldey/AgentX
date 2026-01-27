# Function Extraction: config/settings.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/config/settings.py`

## File Size
97 lines

## Purpose

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "

## Key Classes
- `Settings`

## Key Functions
- `get_settings()`

## Dependencies
- from functools import lru_cache
- from pydantic_settings import BaseSettings, SettingsConfigDict

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 1 functions.
It uses synchronous operations.
Code complexity: 41 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.517502
- Lines of code: 41

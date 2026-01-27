# Function Extraction: main.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/main.py`

## File Size
97 lines

## Purpose
    # Startup
    logger.info(
        f"{settings.app_name} v{settings.app_version} starting on {settings.host}:{settings.port}"
    )
    logger.info(f"LLM: {settings.llm_provider}/{settings.llm_mod

## Key Classes
None

## Key Functions
- async `lifespan()`
- async `root()`
- `main()`

## Dependencies
- import logging
- from contextlib import asynccontextmanager
- from typing import AsyncGenerator
- import uvicorn
- from fastapi import FastAPI
- from fastapi.middleware.cors import CORSMiddleware
- from api.routes import router
- from config.settings import settings
- from config.dspy import configure_dspy

## Data Structures
See key classes above

## Business Logic
This module contains 0 classes and 3 functions.
It focuses on async operations.
Code complexity: 63 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.520065
- Lines of code: 63

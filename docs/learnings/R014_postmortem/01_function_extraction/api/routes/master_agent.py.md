# Function Extraction: api/routes/master_agent.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/api/routes/master_agent.py`

## File Size
146 lines

## Purpose

    Implements the complete R014 Master-Agent pipeline with 10 phases.

## Key Classes
None

## Key Functions
- async `generate_widget_master_agent()`
- async `send_widget()`
- async `send_qa_progress()`
- `_serialize_delivery_plan()`

## Dependencies
- import logging
- import uuid
- from typing import Any
- from fastapi import WebSocket, WebSocketDisconnect
- from application.use_cases.master_agent import get_master_agent_use_case
- from api.mock_handler import handle_mock_mode
- from config.settings import settings

## Data Structures
See key classes above

## Business Logic
This module contains 0 classes and 4 functions.
It focuses on async operations.
Code complexity: 114 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.513436
- Lines of code: 114

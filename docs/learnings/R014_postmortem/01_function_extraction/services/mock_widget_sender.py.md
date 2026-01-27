# Function Extraction: services/mock_widget_sender.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/mock_widget_sender.py`

## File Size
147 lines

## Purpose

Run with: uv run python services/mock_widget_sender.py

This script connects to the frontend WebSocket endpoint and sends pre-crafted
widget data without making LLM calls, allowing isolated frontend 

## Key Classes
- `MockWidgetSender`

## Key Functions
- async `send_widgets()`
- `__init__()`
- `_prepare_widget()`

## Dependencies
- import asyncio
- import json
- import logging
- from datetime import datetime
- import websockets
- from services.mock_widget_repository import MockWidgetRepository
- from services.mock_widget_sender_cli import main

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 3 functions.
It focuses on async operations.
Code complexity: 91 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.530407
- Lines of code: 91

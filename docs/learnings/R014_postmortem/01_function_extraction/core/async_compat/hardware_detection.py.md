# Function Extraction: core/async_compat/hardware_detection.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/core/async_compat/hardware_detection.py`

## File Size
80 lines

## Purpose

    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"


def detect_hardware_tier() -> str:

## Key Classes
- `HardwareTier`

## Key Functions
- `detect_hardware_tier()`
- `should_use_async()`

## Dependencies
- import logging
- import torch
- from config.settings import settings

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 2 functions.
It uses synchronous operations.
Code complexity: 55 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.518516
- Lines of code: 55

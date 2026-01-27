# Function Extraction: services/widget_spawner/intelligent_agent.py

## File Path
`/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/widget_spawner/intelligent_agent.py`

## File Size
126 lines

## Purpose
    Intelligent UI generator using three-tier architecture.

    Tier 1: Context Analyzer - Understand the situation
    Tier 2: Presentation Planner - Decide HOW to present
    Tier 3: Content Genera

## Key Classes
- `IntelligentUIGenerator`

## Key Functions
- `__init__()`
- `forward()`

## Dependencies
- import json
- import logging
- import uuid
- from typing import Dict, Any
- import dspy
- from services.widget_spawner.context_analyzer import ContextAnalyzerAgent
- from services.widget_spawner.presentation_planner import PresentationPlannerAgent
- from services.widget_spawner.enhanced_executor import EnhancedExecutorAgent

## Data Structures
See key classes above

## Business Logic
This module contains 1 classes and 2 functions.
It uses synchronous operations.
Code complexity: 93 lines of executable code.

## Integration Points
See dependencies above

## Notes
- Extracted on: 2026-01-27T12:52:56.564324
- Lines of code: 93

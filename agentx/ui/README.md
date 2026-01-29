# UI Layer

**Purpose**: UI descriptors and WebSocket protocols for server-driven UI.

## Structure

- `descriptors/`: UI descriptor classes (BaseUIDescriptor, MarkdownDescriptor, etc.)
- `protocols/`: WebSocket message schemas

## Server-Driven UI Pattern (C007)

Backend emits UI components via `push_ui_message()` which flow through:
1. LangGraph State (AgentState.ui field with ui_message_reducer)
2. useStream() hook in frontend
3. LoadExternalComponent rendering
4. ui.tsx widget registry (colocated in agent/ directory)

## Files

- `base.py`: BaseUIDescriptor, CardDescriptor, and base descriptor classes
- `markdown_block.py`: MarkdownBlockDescriptor specialized class
- `websocket_messages.py`: All WebSocket message types (Query, Response, UIComponent, etc.)

## 12 Frozen Widget Types

markdown, card, form, progress, action, confirmation, voice, image, gallery, chart, searchResult, hopProgress, citationCard

# executor_helpers.py - Function Extraction

## File: services/widget_spawner/executor_helpers.py

### Primary Purpose
Helper functions for widget executor - handles image and gallery widget generation with dual search.

### Key Functions

#### `generate_image_widget(context: str, widget_id: str, image_search: SearXNGSearchModule) -> dict`
**Purpose**: Generate image widget with both text and image search.

**Logic**:
1. Search for text content: `image_search(query=context, search_type="general")`
2. Search for images: `image_search(query=context, search_type="images")`
3. Extract url_list from both results
4. Build image widget with image_urls and text_context

**Returns**: Widget data dictionary.

---

#### `generate_gallery_widget(context: str, widget_id: str, image_search: SearXNGSearchModule) -> dict`
**Purpose**: Generate gallery widget with both text and image search.

**Logic**: Same as image_widget, but uses build_gallery_widget.

**Returns**: Widget data dictionary.

---

### Architectural Patterns

1. **Dual search**: Both general and image search for richer context
2. **Helper functions**: Extracted from executor for modularity
3. **URL list extraction**: Uses get("url_list", []) for safety

---

### Dependencies

**Internal**:
- `services.tools.researcher.searxng_search`: SearXNGSearchModule
- `services.widget_spawner.builders`: build_gallery_widget, build_image_widget

**External**:
- `logging`: Standard logging

---

### Lessons Learned

1. **Dual search enriches context**: General + image search = better widgets
2. **Image widgets need both**: Text context provides caption/alt text
3. **Helper extraction**: Keeps executor.py focused on orchestration
4. **Safe get pattern**: Use .get() for optional fields

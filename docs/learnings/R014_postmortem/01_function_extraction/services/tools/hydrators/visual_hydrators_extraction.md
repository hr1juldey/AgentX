# Function Postmortem: services/tools/hydrators/visual_hydrators.py

## Metadata
- **File**: services/tools/hydrators/visual_hydrators.py
- **Lines of Code**: 105
- **Purpose**: Hydrates image and gallery widgets with real image search
- **Dependencies**: `logging`, `dspy`, `services.tools.researcher.searxng_search.SearXNGSearchModule`

---

## Analysis

**File Status**: PRODUCTION DSPy MODULE

**Purpose**: Provides DSPy modules for hydrating image and gallery widgets by searching SearXNG for images and building appropriate widget descriptors.

---

## Classes Extracted

### `ImageHydratorModule(dspy.Module)`

**Purpose**: Hydrates image widgets with image URLs from SearXNG search.

**Constructor**: `__init__(self)`
- Initializes `SearXNGSearchModule` for image search

**Method**: `forward(self, presentation_ready: dict) -> dict`

**Parameters**:
- `presentation_ready: dict` - Contains query and research data

**Returns**: `dict` - Image widget descriptor with:
- `descriptor_type: "image"`
- `content: str` - Image URL
- `title: str` - Image title
- `metadata: dict` - Optional caption

**Algorithm**:
1. Perform both general and image search
2. Extract first image from image_list
3. Extract caption from text search results
4. Build image widget descriptor
5. Fallback to error widget if no images found

**Dual Search Strategy**:
```python
text_result = self.image_search(query=query, search_type="general")
image_result = self.image_search(query=query, search_type="images")
```

**Why Two Searches?**
- Image search: Gets image URLs
- General search: Gets captions/context for images

**Fallback Behavior**:
```python
if not image_list or len(image_list) == 0:
    return {
        "descriptor_type": "image",
        "content": "",
        "metadata": {"error": "No images found"},
    }
```

---

### `GalleryHydratorModule(dspy.Module)`

**Purpose**: Hydrates gallery widgets with multiple images from SearXNG search.

**Constructor**: `__init__(self)`
- Initializes `SearXNGSearchModule` for image search

**Method**: `forward(self, presentation_ready: dict) -> dict`

**Parameters**:
- `presentation_ready: dict` - Contains query and research data

**Returns**: `dict` - Gallery widget descriptor with:
- `descriptor_type: "gallery"`
- `content: list` - Gallery items (max 8)
- `title: "Image Gallery"`
- `metadata: dict` - Optional description

**Algorithm**:
1. Perform both general and image search
2. Build gallery items from image_list (max 8)
3. Extract description from text search results
4. Build gallery widget descriptor

**Gallery Item Structure**:
```python
{
    "url": str,
    "title": str,
    "caption": str  # Truncated to 100 chars
}
```

**Max Limit**: 8 images (prevents overwhelming UI)

**Logging**: Logs image count and query preview

---

## File Summary

**Total Classes**: 2 (both DSPy Modules)
**Lines of Code**: 105

**Overall Assessment**: Clean hydrator pattern for visual widgets. Good use of dual search for images + captions.

**Key Learnings for Real AgentX**:
1. ✅ **Dual search strategy**: Image search for URLs, general search for context
2. ✅ **Fallback handling**: Returns error widget instead of crashing
3. ✅ **Max limits**: Gallery capped at 8 images (performance)
4. ✅ **Caption truncation**: Prevents overly long captions
5. ✅ **Logging**: Logs result counts for debugging
6. ✅ **DSPy Module pattern**: Standard forward() interface

**Reuse for Real AgentX**: ✅ **HIGH PRIORITY**
- Pattern for any media hydrator
- Use for:
  - Image widgets (current)
  - Gallery widgets (current)
  - Video widgets (modify for video search)
  - Audio widgets (modify for audio search)
- Modify for different image sources:
  - SearXNG (current - privacy-focused)
  - Unsplash API
  - Pexels API
  - Google Images API

**Potential Improvements**:
- Add image dimension filtering (min width/height)
- Add image format filtering (JPG, PNG, WebP)
- Add safe search filtering
- Add image caching (URLs expire)
- Add alt text generation for accessibility
- Add image quality scoring
- Add duplicate detection (same image from multiple sources)

**Integration**:
- Used by: HydrationCoordinator
- Depends on: SearXNGSearchModule
- Output: Widget descriptors for frontend

**Widget Descriptor Pattern**:
```python
{
    "descriptor_type": "image" | "gallery",
    "content": str | list,
    "title": str,
    "metadata": dict  # Optional
}
```

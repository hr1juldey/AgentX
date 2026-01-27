# Function Postmortem: api/generators/media_widgets.py

## Metadata
- **File**: prototypes/R014_ui_showcase/backend/api/generators/media_widgets.py
- **Lines of Code**: 84
- **Purpose**: Generate content for image, gallery, and chart widgets
- **Dependencies**: dspy, api.dspy_signatures, api.models

---

## Analysis

**Status**: Working async widget generators for media components

**Purpose**: Contains static async methods that use DSPy to generate content for media widgets (images, galleries, charts).

**Architecture**: Static method pattern - stateless generators

---

## Functions/Classes Extracted

### MediaWidgetGenerator (class)

**Purpose**: Generate content for media-based widgets

**Pattern**: Static methods only - no instance state

---

### generate_image (staticmethod)

**Purpose**: Generate image widget with title, caption, and URL

**Signature**: `async def generate_image(prompt: str) -> UIDescriptor`

**Lines**: 22-36

**Key Code**:
```python
@staticmethod
async def generate_image(prompt: str) -> UIDescriptor:
    generator = dspy.Predict(ImageContentSignature)
    result = generator(subject=prompt)
    return UIDescriptor(
        id=f"image-{datetime.now().timestamp()}",
        type="image",
        timestamp=datetime.now().isoformat(),
        title=result.title,
        content=result.caption,
        metadata={
            "image_url": f"https://picsum.photos/800/600?random={datetime.now().timestamp()}"
        },
    )
```

**What Works**:
- Uses Picsum for placeholder images
- Timestamp in URL prevents caching
- LLM generates title and caption
- Simple and effective

**Mistakes Found**:
- Always uses Picsum - no option for real images
- Fixed dimensions (800x600) - not configurable
- No alt text for accessibility

**Behavioral Notes**:
- Each call generates unique URL
- No image validation
- No error handling for bad URLs

**Dependencies**:
- dspy.Predict
- ImageContentSignature
- UIDescriptor

**Reusability**: MEDIUM - Good for demos, needs production options

---

### generate_gallery (staticmethod)

**Purpose**: Generate gallery widget with multiple images

**Signature**: `async def generate_gallery(prompt: str) -> UIDescriptor`

**Lines**: 38-69

**Key Code**:
```python
@staticmethod
async def generate_gallery(prompt: str) -> UIDescriptor:
    generator = dspy.Predict(GalleryContentSignature)
    result = generator(theme=prompt)
    return UIDescriptor(
        id=f"gallery-{datetime.now().timestamp()}",
        type="gallery",
        timestamp=datetime.now().isoformat(),
        title=result.title,
        content=result.description,
        metadata={
            "images": [
                {
                    "url": "https://picsum.photos/seed/nature1/400/400",
                    "title": "Nature Scene",
                },
                {
                    "url": "https://picsum.photos/seed/nature2/400/400",
                    "title": "Landscape",
                },
                {
                    "url": "https://picsum.photos/seed/nature3/400/400",
                    "title": "Water View",
                },
                {
                    "url": "https://picsum.photos/seed/nature4/400/400",
                    "title": "Mountain",
                },
            ]
        },
    )
```

**What Works**:
- Hardcoded gallery with nature theme
- Consistent image dimensions
- Picsum seed ensures reproducibility

**Mistakes Found**:
- Images are completely hardcoded - ignores LLM output
- Theme is requested from LLM but never used
- Number of images is fixed (4)
- No way to customize gallery content

**Behavioral Notes**:
- LLM generates title/description but images are static
- Seeds (nature1-4) ensure same images load
- No dynamic gallery sizing

**Dependencies**:
- dspy.Predict
- GalleryContentSignature
- UIDescriptor

**Reusability**: LOW - Too much hardcoding, ignores LLM output

---

### generate_chart (staticmethod)

**Purpose**: Generate chart widget with title and description

**Signature**: `async def generate_chart(prompt: str) -> UIDescriptor`

**Lines**: 71-83

**Key Code**:
```python
@staticmethod
async def generate_chart(prompt: str) -> UIDescriptor:
    generator = dspy.Predict(ChartContentSignature)
    result = generator(data_topic=prompt)
    return UIDescriptor(
        id=f"chart-{datetime.now().timestamp()}",
        type="chart",
        timestamp=datetime.now().isoformat(),
        title=result.title,
        content=result.description,
        metadata={"chart_type": "bar"},
    )
```

**What Works**:
- LLM generates contextual title and description
- Simple metadata structure

**Mistakes Found**:
- Chart type is hardcoded to "bar"
- No actual chart data - just metadata
- No configuration for chart options
- Missing data series, axes, etc.

**Behavioral Notes**:
- Generates description but no visualization data
- Would need separate hydrator to populate chart data
- Very minimal implementation

**Dependencies**:
- dspy.Predict
- ChartContentSignature
- UIDescriptor

**Reusability**: LOW - Missing critical chart data

---

## File Summary

**Assessment**: Mixed quality implementation. Image generator is good, but gallery and chart generators are incomplete with too much hardcoding.

**Key Learnings**:
1. Picsum is good for placeholder images
2. Timestamp-based URLs prevent caching
3. Seeded URLs provide reproducibility
4. Hardcoded data limits reusability significantly

**Mistakes to Avoid**:
1. Don't ignore LLM output (gallery ignores theme)
2. Don't hardcode what should be dynamic
3. Don't generate incomplete widgets (chart has no data)
4. Don't fix configuration values

**Recommendations**:
1. Gallery: Use LLM theme to select image categories
2. Chart: Add data generation or use chart hydrator
3. All: Add config parameters for customization
4. All: Make metadata fields dynamic

**Reusability Score**: LOW-MEDIUM - Image is good, gallery/chart need work

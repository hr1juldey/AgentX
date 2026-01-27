# Function Postmortem: api/routes/widget_routes/mock.py

## Metadata
- **File**: prototypes/R014_ui_showcase/backend/api/routes/widget_routes/mock.py
- **Lines of Code**: 53
- **Purpose**: Legacy mock widget generation endpoints
- **Dependencies**: api.content_generator, api.models

---

## Analysis

**Status**: Legacy endpoint maintained for backward compatibility

**Purpose**: Provides simple mock widget generation using ContentGenerator facade. Superseded by master agent pipeline.

**Architecture**: Simple POST endpoint with if-elif chain

---

## Functions/Classes Extracted

### generate_content (POST endpoint)

**Purpose**: Generate UI content using DSPy + Ollama (legacy endpoint)

**Signature**: `async def generate_content(request: GenerateRequest) -> UIDescriptor`

**Lines**: 18-52

**Key Code**:
```python
@router.post("/mock/generate")
async def generate_content(request: GenerateRequest) -> UIDescriptor:
    """Generate UI content using DSPy + Ollama (legacy endpoint)."""
    generator = ContentGenerator()

    try:
        if request.widget_type == "markdown":
            return await generator.generate_markdown(request.prompt)
        elif request.widget_type == "card":
            return await generator.generate_card(request.prompt)
        elif request.widget_type == "form":
            return await generator.generate_form(request.prompt)
        elif request.widget_type == "progress":
            return await generator.generate_progress(request.prompt)
        elif request.widget_type == "action":
            return await generator.generate_action(request.prompt)
        elif request.widget_type == "confirmation":
            return await generator.generate_confirmation(request.prompt)
        elif request.widget_type == "image":
            return await generator.generate_image(request.prompt)
        elif request.widget_type == "gallery":
            return await generator.generate_gallery(request.prompt)
        elif request.widget_type == "chart":
            return await generator.generate_chart(request.prompt)
        else:
            raise ValueError(f"Unknown widget type: {request.widget_type}")
    except Exception as e:
        return UIDescriptor(
            id=f"error-{datetime.now().timestamp()}",
            type=request.widget_type or "markdown",
            timestamp=datetime.now().isoformat(),
            title="Generation Error",
            content=f"Could not generate content: {str(e)}",
            metadata={"error": True},
        )
```

**What Works**:
- Simple interface
- ContentGenerator facade usage
- Error widget on failure
- Covers all widget types

**Mistakes Found**:
- Long if-elif chain - should use dict dispatch
- No validation of prompt
- Generator instantiated every request
- Not using application layer

**Behavioral Notes**:
- Directly uses ContentGenerator
- Bypasses application layer
- Returns error widget on failure
- No streaming support

**Dependencies**:
- ContentGenerator
- GenerateRequest
- UIDescriptor

**Reusability**: LOW - Legacy pattern, not recommended

---

## File Summary

**Assessment**: Legacy endpoint that works but should be replaced with application layer pattern.

**Key Learnings**:
1. If-elif chains don't scale well
2. Direct generator usage bypasses layers
3. Error widgets are better than exceptions
4. Legacy endpoints need clear deprecation notices

**Mistakes to Avoid**:
1. Don't use long if-elif chains - use dict dispatch
2. Don't bypass application layer
3. Don't instantiate generators per request

**Recommendations**:
1. Use dict dispatch for widget types
2. Add deprecation notice
3. Route to application layer
4. Make generator a singleton

**Better Pattern**:
```python
GENERATORS = {
    "markdown": ContentGenerator.generate_markdown,
    "card": ContentGenerator.generate_card,
    # ...
}

generator_func = GENERATORS.get(request.widget_type)
if not generator_func:
    raise ValueError(f"Unknown widget type: {request.widget_type}")
return await generator_func(request.prompt)
```

**Reusability Score**: LOW - Legacy pattern, use application layer instead

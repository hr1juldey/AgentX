# Function Postmortem: services/tools/researcher/content_filter.py

## Metadata
- **File**: services/tools/researcher/content_filter.py
- **Lines of Code**: 134
- **Purpose**: DSPy module for filtering relevant content from web pages
- **Dependencies**: `dspy`, `services.tools.researcher.link_parser`

---

## Analysis

**File Status**: PRODUCTION DSPy MODULE

**Purpose**: Filters web content to find only relevant parts for research goal. Uses two DSPy predictors: FilterRelevantContent (extract relevant sentences) and ExtractRelevantLinks (identify links worth following).

---

## Classes Extracted

### DSPy Signatures

**`class FilterRelevantContent(dspy.Signature)`**
- **Input Fields**:
  - `content_chunk: str` - Web page content (max 2000 chars)
  - `goal: str` - Research goal or question we're trying to answer
- **Output Fields**:
  - `relevant_content: str` - Only the relevant sentences that directly address the goal. If nothing relevant, output 'NONE'. Keep original wording.
- **Description**: "Filter content to find only relevant parts for the research goal. Input: A chunk of web page content (max 2000 chars) + research goal. Output: Only the relevant sentences/paragraphs that help answer the goal."
- **Examples in docstring**: Shows filtering privacy policy, pricing, AI technology queries

**`class ExtractRelevantLinks(dspy.Signature)`**
- **Input Fields**:
  - `links_summary: str` - List of links in format: URL | Text (max 10 links)
  - `goal: str` - Research goal or question we're trying to answer
- **Output Fields**:
  - `relevant_urls: str` - URLs worth following, one per line with | and brief reason. Example: 'https://example.com/page | Has detailed guide on topic'. Max 3 URLs. If none relevant, output 'NONE'.
- **Description**: "Identify which links are worth following based on research goal. Input: List of link descriptions (URL + text) + research goal. Output: URLs that are likely to contain relevant information."

### DSPy Modules

**`class ContentFilterModule(dspy.Module)`**
- **Purpose**: Filters web content to find relevant parts for research goal
- **Constants**:
  - `MAX_CONTENT_LENGTH = 2000` - Prevents context overflow
- **Attributes**:
  - `self.content_filter: dspy.Predict(FilterRelevantContent)` - Content filtering predictor
  - `self.link_extractor: dspy.Predict(ExtractRelevantLinks)` - Link extraction predictor
- **Methods**:
  - **`__init__(self)`**: Initializes both predictors with `dspy.Predict()`
  - **`filter_content(self, page_content: str, goal: str) -> str`**:
    - Truncates content to `MAX_CONTENT_LENGTH`
    - Calls `self.content_filter(content_chunk=chunk, goal=goal)`
    - Extracts `result.relevant_content`
    - Returns empty string if `relevant.strip().upper() == "NONE"`
    - Returns `relevant.strip()` otherwise
  - **`extract_links(self, links: list[dict], goal: str) -> list[dict]`**:
    - Returns empty list if `not links`
    - Builds links_summary: `"\n".join([f"{link['url']} | {link.get('text', '')[:80]}" for link in links[:10]])`
    - Calls `self.link_extractor(links_summary=links_summary, goal=goal)`
    - Extracts `result.relevant_urls`
    - Calls `parse_relevant_links(relevant_urls, links)` helper
    - Returns list of relevant link dicts with 'reason' field added (max 3)

---

## File Summary

**Total Classes**: 3 (2 DSPy Signatures, 1 DSPy Module)
**Lines of Code**: 134

**Overall Assessment**: Well-structured DSPy module with clear separation of concerns. Good examples in docstrings guide LLM behavior. "NONE" fallback prevents hallucination. Link limit (10 in, 3 out) prevents explosion.

**Key Learnings for Real AgentX**:
1. ✅ **Two-stage filtering**: Content filtering + link extraction for comprehensive processing
2. ✅ **"NONE" fallback**: Explicit signal when no relevant content found
3. ✅ **Content truncation**: 2000 char limit prevents context overflow
4. ✅ **Link limits**: 10 links in → 3 links out prevents explosion
5. ✅ **Original wording preservation**: Keeps text authenticity, avoids paraphrasing
6. ✅ **Reason field**: Explains why each link is relevant
7. ⚠️ **Tight coupling**: Depends on `parse_relevant_links` helper from another module

**Reuse for Real AgentX**: ✅ HIGH - Core pattern for content filtering and link extraction. DSPy signatures are reusable. Consider adding confidence scores, multiple categories, and configurable limits.

# data_tracking.py - Function Extraction

## File: `services/master_agent/orchestration/data_tracking.py`

## Purpose
Strategic loggers for detecting data loss/leak across pipeline stages. Tracks data flow and validates data integrity.

---

## Functions

### `_log_list_counts(label: str, data: dict, keys: list[str]) -> None`
**Purpose**: Log counts for specified list keys in data dict.

**Parameters**:
- `label` (str): Section label for grouping
- `data` (dict): Data dictionary to extract counts from
- `keys` (list[str]): List of keys to count

**Returns**: None

**Behavior**:
- Iterates through specified keys
- Logs count of items if value is a list
- Logs type name if value is not a list
- Uses indented logging format (4 spaces for label, 6 spaces for items)

**Mistakes/Issues**:
- None - straightforward logging utility

**Usage Notes**:
- Used by all tracking functions to standardize list logging
- Handles both list and non-list values gracefully

---

### `track_contextualizer_output(result: dict) -> None`
**Purpose**: Track data leaving contextualizer phase. Logs counts of all arrays and presence of key fields.

**Parameters**:
- `result` (dict): Contextualizer output result

**Returns**: None

**Behavior**:
- Logs "beautiful_data" arrays (key_facts, trends, comparisons, extracted_numbers)
- Logs core_data fields:
  - contextualized_data (document count)
  - citations (item count)
  - structured_data (key count)
  - query (boolean and length)
  - search_terms (item count + sample of first 2)

**Mistakes/Issues**:
- None - comprehensive tracking

**Usage Notes**:
- Called after contextualizer phase completes
- Critical for detecting if contextualizer dropped data
- Sample of search_terms helps verify search quality

---

### `track_research_merge(first: dict, additional: dict, merged: dict) -> None`
**Purpose**: Track research merge operation with before/after comparison. Detects data loss by comparing merged counts against inputs.

**Parameters**:
- `first` (dict): First contextualized research result (primary)
- `additional` (dict): Additional contextualized research result
- `merged` (dict): Merged contextualized research result

**Returns**: None

**Behavior**:
- Counts documents before merge (first + additional)
- Counts documents after merge (merged)
- Counts citations before merge
- Counts citations after merge
- Logs before/after comparison
- **Detects data loss**: Warns if merged_docs < max(first_docs, add_docs)
- **Detects data loss**: Warns if merged_cites < max(first_cites, add_cites)

**Mistakes/Issues**:
- **Critical**: This is the PRIMARY data loss detection mechanism
- Uses max() instead of sum() because merge should preserve unique items, not add them
- Warning if merged < max indicates merge is dropping items

**Usage Notes**:
- Called by merge_research_results() after merging
- Essential for validating merge logic is working correctly
- Should be tested with duplicate and non-duplicate datasets

---

### `track_presenter_input(researched_data: dict) -> None`
**Purpose**: Track data entering presenter phase (hydrators receive this). Logs what data is available to chart/markdown/card hydrators.

**Parameters**:
- `researched_data` (dict): Research data from contextualizer

**Returns**: None

**Behavior**:
- Logs beautiful_data arrays (used by all hydrators)
- Logs other_fields:
  - structured_data keys (first 5)
  - citations count
  - query (first 50 chars + length)
  - url_list count

**Mistakes/Issues**:
- None - comprehensive tracking

**Usage Notes**:
- Called before presenter phase
- Shows what data hydrators will have access to
- Helps debug missing data in hydrated widgets

---

## Patterns and Lessons

### Data Tracking Pattern
1. **Log before/after counts** for all transformation operations
2. **Detect data loss** by comparing output vs input
3. **Log samples** of key arrays (first 2-3 items)
4. **Track structure**: keys, counts, lengths
5. **Use warnings** for data loss (not errors, but critical)

### What Works
- **Simple counting**: Just count items before/after
- **max() comparison**: Detects if merge is dropping unique items
- **Sample logging**: Shows actual data, not just counts
- **Structured logging**: Label sections clearly with indentation

### What Doesn't Work
- **No validation of data content** - only tracks counts
- **No tracking of individual documents** - can't tell WHICH documents were lost
- **No historical tracking** - can't see trends across multiple runs

### Critical Detection Logic
```python
# Data loss detection
if merged_docs < max(first_docs, add_docs):
    logger.warning("⚠️  DATA LOSS: Documents decreased")
```

This pattern is essential for any multi-stage pipeline where data transforms between stages.

---

## Dependencies
- `logging` - Standard logging

## Used By
- `early_phases.py` - track_contextualizer_output()
- `research_merger.py` - track_research_merge()
- `late_phases.py` - track_presenter_input()

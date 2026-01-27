# Function Postmortem: services/tools/researcher/multihop_reader.py

## Metadata
- **File**: services/tools/researcher/multihop_reader.py
- **Lines of Code**: 145
- **Purpose**: Multi-hop web reader with n² report generation
- **Dependencies**: `logging`, `services.tools.researcher.content_filter`, `services.tools.researcher.multihop_basic`, `services.tools.researcher.multihop_processor`, `services.tools.researcher.report_generator`

---

## Analysis

**File Status**: PRODUCTION DSPy MODULE

**Purpose**: "Z-read on steroids" - Multi-hop web reader generating n² micro reports. Formula: Total reports = n² where n = number of hops (e.g., 3 hops → 9 reports total). Two modes: Basic (single URL) and Multi-hop (recursive link following).

---

## Classes Extracted

### DSPy Modules (Orchestrator)

**`class MultiHopReader`**
- **Purpose**: Multi-hop web reader generating n² micro reports
- **Constants**:
  - `MIN_HOPS = 3` - Minimum hops
  - `MAX_HOPS = 5` - Maximum hops
  - `DEFAULT_HOPS = 3` - Default hops
  - `MAX_CONTENT_LENGTH = 2000` - Content limit per page
  - `MAX_REPORTS_PER_PAGE = 3` - Max reports per page
- **Attributes**:
  - `self.filter: ContentFilterModule` - Content filtering instance
  - `self.reporter: ReportGeneratorModule` - Report generation instance
- **Methods**:
  - **`__init__(self)`**: Initializes `self.filter = ContentFilterModule()`, `self.reporter = ReportGeneratorModule()`
  - **`async def basic_read(self, url: str, goal: str) -> dict`**:
    - Delegates to `basic_read(url, goal, self.filter, self.reporter)`
    - Returns dict with url, title, relevant_content, report
  - **`async def multihop_read(self, urls: list[str], goal: str, max_hops: int = DEFAULT_HOPS) -> dict`**:
    - Clamps max_hops: `max(MIN_HOPS, min(max_hops, MAX_HOPS))`
    - Calculates target reports: `target_reports = max_hops**2`
    - Logs start: `[MULTIHOP] Starting: {max_hops} hops → {target_reports} reports target`
    - Initializes:
      - `all_reports: list[dict] = []`
      - `all_citations: list[dict] = []`
      - `trajectory: list[dict] = []`
      - `reports_per_level = target_reports // max_hops`
      - `hop_counts = {i: 0 for i in range(1, max_hops + 1)}`
      - `queue = initialize_multihop_queue(urls)`
      - `seen_urls = set(urls)`
    - **BFS Loop** (`while queue and len(all_reports) < target_reports`):
      1. Popleft: `url, hop_level = queue.popleft()`
      2. Skip if `hop_level > max_hops`
      3. Call `process_hop(...)` → `traj_entry, report_dict, citation_dict, link_dicts`
      4. Append `traj_entry` to trajectory
      5. If `report_dict` and `report_dict["report"]`:
         - Append to all_reports with hop_level and source_title
         - Increment `hop_counts[hop_level]`
         - Append citation_dict to all_citations
      6. If `link_dicts`:
         - For each link: add to seen_urls, append to queue with `hop_level + 1`
      7. Log progress: `[HOP {hop_level}] Reports so far: {len(all_reports)}/{target_reports}`
    - Logs completion: `[MULTIHOP] Complete: {len(all_reports)} reports from {max_hops} hops`
    - Returns dict:
      ```python
      {
          "all_reports": all_reports,
          "total_count": len(all_reports),
          "citations": all_citations,
          "trajectory": trajectory,
          "hop_distribution": hop_counts,
          "target_reports": target_reports,
      }
      ```

**n² Formula Explained**:
- Total reports = n² where n = hops
- Example: 3 hops → 9 reports total (NOT cumulative)
- Reports distributed across pages: `reports_per_level = target_reports // max_hops`
- Context limits: 2000 chars per page, only filtered content sent to LLM
- Max 3 links per page to prevent explosion

---

## File Summary

**Total Classes**: 1 (orchestrator class)
**Lines of Code**: 145

**Overall Assessment**: Sophisticated multi-hop traversal orchestrator. n² formula is unique approach to report generation. BFS queue with seen_urls prevents cycles. Trajectory logging enables debugging. Good quota management prevents runaway generation.

**Key Learnings for Real AgentX**:
1. ✅ **n² report generation**: Total reports = hops² (e.g., 3 hops → 9 reports)
2. ✅ **BFS traversal**: Queue-based with hop_level tracking prevents infinite loops
3. ✅ **Cycle prevention**: seen_urls set prevents revisiting pages
4. ✅ **Quota management**: reports_per_level limits output per hop level
5. ✅ **Trajectory logging**: Complete history of visited pages and status
6. ✅ **Two modes**: Basic (single URL) and Multi-hop (recursive)
7. ✅ **Hop distribution tracking**: hop_counts shows reports per level
8. ⚠️ **Fixed target**: May not reach target_reports if not enough relevant content
9. ⚠️ **No timeout**: Infinite loop possible if queue never empties (unlikely with seen_urls)

**Reuse for Real AgentX**: ✅ HIGH - Advanced pattern for recursive web reading. n² formula is innovative but may need tuning. BFS with cycle prevention is reusable. Consider adding timeouts, adaptive targets, and priority scoring for link selection.

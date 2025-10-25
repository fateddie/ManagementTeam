# Feature Audit Checklist

Use this checklist when adding ANY new analysis, intelligence, or decision-support feature to the system.

**Purpose:** Ensure every feature follows the core principles in `PRINCIPLES.md` for transparency, human control, and auditability.

---

## Quick Start

1. Copy this template for your feature
2. Check each box as you implement
3. Review all sections before marking feature complete
4. If ANY box is unchecked, the feature is NOT ready

---

## Feature Information

**Feature Name:** `[e.g., "Competitor Intelligence Analyzer"]`

**Purpose:** `[What insight does this provide?]`

**Owner:** `[Your name]`

**Date Started:** `[YYYY-MM-DD]`

**Status:** `[ ] In Progress  [ ] Ready for Review  [ ] Complete`

---

## ✅ TRANSPARENCY CHECKLIST

### Data Visibility

- [ ] Raw data is preserved (not just aggregated summaries)
- [ ] User can access full dataset used in analysis
- [ ] UI/CLI provides way to view source data
- [ ] No lossy summarization (original data is retained)

**How to verify:** Run feature → Ask "Can I see the raw data?" → Should be YES

### Source References

- [ ] Every metric includes `source_posts` or `source_ids` array
- [ ] Aggregate counts link back to individual records
- [ ] Example quotes/text provided alongside metrics
- [ ] Click-through or command to view source data implemented

**Example:**
```json
{
  "competitor": "Sonant",
  "mentions": 2,
  "source_posts": [96, 102],
  "example_quotes": ["I'm using Sonant for english calls..."]
}
```

### Confidence Display

- [ ] Confidence level shown for every insight (high/medium/low)
- [ ] Uncertainty acknowledged when present
- [ ] Sample size displayed prominently
- [ ] Limitations called out explicitly

**Example:** "MEDIUM confidence (only 4 posts)" vs pretending certainty

### Interactive Exploration

- [ ] User can filter/search the underlying data
- [ ] Sortable views provided (by urgency, date, upvotes, etc.)
- [ ] Drill-down capability (click industry → see all posts)
- [ ] Multiple views of same data supported

---

## ✅ HUMAN CONTROL CHECKLIST

### Decision Authority

- [ ] No auto-execution of decisions (human must approve)
- [ ] Decision prompts presented with options
- [ ] Checkboxes/ratings provided for human input
- [ ] System recommends but does NOT decide

**Anti-pattern to avoid:** `self.state.target_icp = best_icp` (auto-selecting)

### Override Capability

- [ ] User can disagree with recommendation
- [ ] User can adjust scoring weights/thresholds
- [ ] User can annotate/tag/note their reasoning
- [ ] Alternative options presented (not just one "correct" answer)

### Configuration Control

- [ ] All weights are in `config.json` (not hard-coded)
- [ ] All thresholds are in `config.json`
- [ ] User can modify config and re-run analysis
- [ ] Defaults are documented with rationale

**Test:** Change a weight in config → Re-run → Verify results update

### Annotation Support

- [ ] User can add notes to insights
- [ ] User can tag/label data points
- [ ] User can rate recommendations (1-5 stars, etc.)
- [ ] Annotations are saved persistently

---

## ✅ AUDITABILITY CHECKLIST

### Audit Trail

- [ ] Every output includes `_audit_trail` section
- [ ] Timestamp in ISO 8601 format included
- [ ] Data source(s) logged
- [ ] Analysis version number included
- [ ] Configuration snapshot saved with results

**Required fields in `_audit_trail`:**
```json
{
  "_audit_trail": {
    "generated_at": "2025-10-25T22:15:00Z",
    "data_source": "social_posts_enriched.csv",
    "total_records": 43,
    "analysis_version": "v2.0",
    "config_file": "config/transparency_config.json",
    "config_snapshot": {...}
  }
}
```

### Reproducibility

- [ ] Analysis can be re-run with same inputs → same outputs
- [ ] Version numbers track changes to analysis logic
- [ ] Configuration is versioned
- [ ] Data snapshots are dated and preserved

**Test:** Re-run analysis with same data/config → Verify identical results

### Decision Logging

- [ ] User decisions are captured and saved
- [ ] Decision rationale can be recorded
- [ ] Decision history is preserved (not overwritten)
- [ ] Decision timestamps logged

**Example storage:** `data/decisions/icp_decision_2025-10-25.json`

### Historical Access

- [ ] Previous analyses are not overwritten (use timestamps)
- [ ] User can compare current vs previous results
- [ ] Data provenance is clear (when was this collected?)
- [ ] Change log available ("What changed since last analysis?")

---

## ✅ EXPORTABILITY CHECKLIST

### Export Formats

- [ ] JSON export supported (machine-readable)
- [ ] CSV export supported (spreadsheet analysis)
- [ ] Excel export supported (rich formatting)
- [ ] Markdown export supported (human-readable reports)

### Export Scope

- [ ] Full dataset export available
- [ ] Filtered subset export available
- [ ] Metadata included in exports (timestamp, source, config)
- [ ] Export includes both raw data AND derived insights

**Test:** Export data → Open in Excel/text editor → Verify completeness

### Export Quality

- [ ] No truncation (full text preserved)
- [ ] No proprietary/locked formats
- [ ] Character encoding handled correctly (UTF-8)
- [ ] Column headers are descriptive

---

## ✅ DOCUMENTATION CHECKLIST

### Code Documentation

- [ ] Docstrings explain purpose and behavior
- [ ] Function signatures clearly typed
- [ ] Comments explain "why" not just "what"
- [ ] Examples provided for complex functions

### User Documentation

- [ ] README updated with new feature
- [ ] Usage examples provided
- [ ] CLI help text accurate
- [ ] UI tooltips/labels clear

### Configuration Documentation

- [ ] Config options documented
- [ ] Defaults explained with rationale
- [ ] Valid ranges specified
- [ ] Impact of changes described

---

## 🧪 VERIFICATION TESTS

### Test 1: Transparency Verification

**Action:** Run the feature and identify one insight (e.g., "4 dental posts")

**Verify:**
- [ ] Can you see all 4 posts?
- [ ] Can you read the full text?
- [ ] Is confidence level shown?
- [ ] Are source IDs provided?

**Pass Criteria:** YES to all questions

### Test 2: Human Control Verification

**Action:** Feature makes a recommendation

**Verify:**
- [ ] Does it present options (not auto-execute)?
- [ ] Can you disagree/override?
- [ ] Can you adjust weights and see impact?
- [ ] Can you save your decision?

**Pass Criteria:** YES to all questions

### Test 3: Audit Trail Verification

**Action:** Generate analysis output

**Verify:**
- [ ] Is there an `_audit_trail` section?
- [ ] Does it include timestamp, version, config?
- [ ] Can you reproduce this analysis later?
- [ ] Is decision history preserved?

**Pass Criteria:** YES to all questions

### Test 4: Export Verification

**Action:** Export the results

**Verify:**
- [ ] Can you export to CSV?
- [ ] Can you export to JSON?
- [ ] Is metadata included?
- [ ] Can you re-import and verify?

**Pass Criteria:** YES to all questions

### Test 5: Six-Month Test

**Hypothetical:** You need to justify this analysis 6 months from now

**Verify:**
- [ ] Can you find the original data?
- [ ] Can you see the exact config used?
- [ ] Can you see your decision and rationale?
- [ ] Can you reproduce the analysis?

**Pass Criteria:** YES to all questions

---

## 🔴 RED FLAGS (Fix Immediately)

If you see ANY of these, STOP and fix:

- ❌ Hard-coded magic numbers (`if score > 70`)
- ❌ Auto-execution without user prompt
- ❌ Aggregate metrics without source IDs
- ❌ No confidence/uncertainty display
- ❌ No `_audit_trail` in output
- ❌ No export functionality
- ❌ Proprietary/locked data formats
- ❌ Pretending certainty when data is sparse

---

## 📊 SCORING RUBRIC

Rate each section 0-5:

| Section | Score (0-5) | Notes |
|---------|-------------|-------|
| **Transparency** | ___ | Can user verify all claims? |
| **Human Control** | ___ | Does user retain decision authority? |
| **Auditability** | ___ | Can this be reproduced later? |
| **Exportability** | ___ | Can data be extracted/analyzed externally? |
| **Documentation** | ___ | Is usage clear? |

**Required:** ≥4 in ALL sections before feature is considered complete.

**Total Score:** `___/25`

- 20-25: Excellent, follows principles
- 15-19: Good, minor improvements needed
- 10-14: Marginal, significant gaps
- <10: Incomplete, not ready

---

## ✅ FINAL SIGN-OFF

Before marking feature as complete:

- [ ] All transparency checklists passed
- [ ] All human control checklists passed
- [ ] All auditability checklists passed
- [ ] All exportability checklists passed
- [ ] All verification tests passed
- [ ] No red flags present
- [ ] Scoring rubric ≥4 in all sections
- [ ] Peer review completed (if applicable)
- [ ] PRINCIPLES.md compliance verified
- [ ] CLAUDE.md patterns followed

**Sign-off:**

**Developer:** `[Name]` **Date:** `[YYYY-MM-DD]`

**Reviewer:** `[Name]` **Date:** `[YYYY-MM-DD]`

---

## 📝 NOTES AND DEVIATIONS

*Document any deviations from the checklist and justification:*

```
[Example: "Export to PDF not implemented due to library complexity.
Markdown export provides equivalent human-readable format."]
```

---

## 🔄 CONTINUOUS IMPROVEMENT

After feature is in production:

- [ ] User feedback collected
- [ ] Usability issues documented
- [ ] Enhancement ideas logged
- [ ] Checklist updated based on learnings

---

**Remember: If you're unsure about ANY checkbox, ask. It's better to over-verify than under-deliver transparency.**

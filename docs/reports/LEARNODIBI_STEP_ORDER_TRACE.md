# LearnODIBI Step Order Trace

**Generated**: 2025-11-02 12:27:55

## Summary

Total files traced: 3

- Total step headers found: 69
- Files with ordering issues: 2
- Total duplicate numbers: 13
- Total gaps in numbering: 0
- Total backward jumps: 0

## Per-File Analysis

### DEVELOPER_WALKTHROUGH_PHASE_1.md

- Total headers: 32
- Current order: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
- ⚠️ **Lexicographic order differs**: [0, 1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 4, 5, 6, 7, 8, 9]

---

### DEVELOPER_WALKTHROUGH_PHASE_2.md

- Total headers: 18
- Current order: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
- ⚠️ **Lexicographic order differs**: [1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 2, 3, 4, 5, 6, 7, 8, 9]

---

### DEVELOPER_WALKTHROUGH_FUNCTIONS.md

- Total headers: 19
- Current order: [1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 4, 5, 5, 6, 6, 6]

**Duplicates (13):**
- Step 1 appears at lines 82 and 122
- Step 1 appears at lines 122 and 234
- Step 1 appears at lines 234 and 335
- Step 1 appears at lines 335 and 453
- Step 1 appears at lines 453 and 574
- Step 2 appears at lines 662 and 762
- Step 2 appears at lines 762 and 823
- Step 3 appears at lines 948 and 1017
- Step 4 appears at lines 1102 and 1192
- Step 4 appears at lines 1192 and 1234
- Step 5 appears at lines 1285 and 1347
- Step 6 appears at lines 1468 and 1662
- Step 6 appears at lines 1662 and 1694

---

## Root Cause Analysis

### Lexicographic vs Numeric Ordering

2 files would have different order if sorted lexicographically.
This suggests the parser is using **numeric ordering** (correct behavior).

### Duplicate Step Numbers

13 duplicate step numbers found across all files.
This is intentional - walkthroughs use section-based numbering.


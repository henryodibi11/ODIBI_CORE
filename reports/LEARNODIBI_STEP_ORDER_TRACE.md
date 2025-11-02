# LearnODIBI Step Order Trace

**Generated**: 2025-11-02 16:34:08

## Summary

Total files traced: 3

- Total step headers found: 65
- Files with ordering issues: 3
- Total duplicate numbers: 6
- Total gaps in numbering: 0
- Total backward jumps: 1

## Per-File Analysis

### DEVELOPER_WALKTHROUGH_PHASE_1.md

- Total headers: 33
- Current order: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
- ⚠️ **Lexicographic order differs**: [0, 1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 4, 5, 6, 7, 8, 9]

---

### DEVELOPER_WALKTHROUGH_PHASE_2.md

- Total headers: 11
- Current order: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
- ⚠️ **Lexicographic order differs**: [1, 10, 11, 2, 3, 4, 5, 6, 7, 8, 9]

---

### DEVELOPER_WALKTHROUGH_FUNCTIONS.md

- Total headers: 21
- Current order: [1, 1, 1, 1, 1, 2, 3, 4, 5, 6, 6, 6, 1, 2, 3, 4, 5, 6, 7, 8, 9]
- ⚠️ **Lexicographic order differs**: [1, 1, 1, 1, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 6, 6, 7, 8, 9]

**Duplicates (6):**
- Step 1 appears at lines 95 and 146
- Step 1 appears at lines 146 and 254
- Step 1 appears at lines 254 and 359
- Step 1 appears at lines 359 and 491
- Step 6 appears at lines 958 and 1088
- Step 6 appears at lines 1088 and 1122

**Backward Jumps (1):**
- Step 6 → 1 at line 1189

---

## Root Cause Analysis

### Lexicographic vs Numeric Ordering

3 files would have different order if sorted lexicographically.
This suggests the parser is using **numeric ordering** (correct behavior).

### Duplicate Step Numbers

6 duplicate step numbers found across all files.
This is intentional - walkthroughs use section-based numbering.

### Backward Jumps

1 instances of step numbers decreasing.
This indicates nested or section-based numbering schemes.


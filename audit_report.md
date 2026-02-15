# CipherCourt Audit Report

**Audit Timestamp:** 2026-02-15T05:33:21.418677
**Framework:** CipherCourt
**Audit Duration:** 0.00 seconds

## Summary

- **Total Connectors:** 5
- **Passed:** 2
- **Failed:** 0
- **Warnings:** 3
- **Not Available:** 0

## Detailed Results

### local_csv_match_results

**Overall Status:** ✅ PASS

#### Availability
**Status:** ✅ PASS

#### Data Quality
**Status:** ✅ PASS

#### Timestamps
**Status:** ✅ PASS

#### Leakage Detection
**Status:** ✅ PASS

---

### local_csv_odds

**Overall Status:** ✅ PASS

#### Availability
**Status:** ✅ PASS

#### Data Quality
**Status:** ✅ PASS

#### Timestamps
**Status:** ✅ PASS

#### Leakage Detection
**Status:** ✅ PASS

---

### match_stats

**Overall Status:** ⚠️ WARNING

#### Availability
**Status:** ✅ PASS

#### Data Quality
**Status:** ⚠️ WARNING

**Issues:**
- Found 50 matches with incomplete stats
- Found 3 statistical inconsistencies

#### Timestamps
**Status:** ⚠️ WARNING

**Issues:**
- Found 2 stats with misaligned timestamps

#### Leakage Detection
**Status:** ✅ PASS

---

### venue_metadata

**Overall Status:** ⚠️ WARNING

#### Availability
**Status:** ✅ PASS

#### Data Quality
**Status:** ⚠️ WARNING

**Issues:**
- Found 15 venues with incomplete metadata
- Found 2 surface type inconsistencies

#### Timestamps
**Status:** ⚠️ WARNING

**Issues:**
- Found 5 venues with stale metadata

#### Leakage Detection
**Status:** ⚠️ WARNING

**Issues:**
- Found 2 suspicious retroactive metadata changes

---

### license_status

**Overall Status:** ⚠️ WARNING

#### Availability
**Status:** ✅ PASS

#### Data Quality
**Status:** ⚠️ WARNING

**Issues:**
- Found 1 incomplete license records

#### Timestamps
**Status:** ⚠️ WARNING

**Issues:**
- Warning: 1 licenses expiring within 30 days

#### Leakage Detection
**Status:** ✅ PASS

---

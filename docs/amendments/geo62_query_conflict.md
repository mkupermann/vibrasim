# GEO-62 — Query-time conflict handling (surface inconsistency, don't silently pick one)

## Motivation
Real KBs contain inconsistencies. GEO-41/52 detect conflicts at WRITE time. At QUERY time, if the store
holds conflicting facts about an entity (same subject, different objects for a functional relation), a
trustworthy system should SURFACE the conflict, not silently return one answer. GEO-62 tests a conflict-aware
query that flags inconsistency.

## Pre-registration (locked BEFORE run)
- Store with some entities having CONSISTENT single facts and some having CONFLICTING facts (e.g. two
  different teams for one person — a data-quality problem).
- Conflict-aware query: gather all same-subject facts (kind=person), if >1 distinct object -> flag CONFLICT
  and return the set; else return the single answer.
- 12 entities: 6 consistent, 6 conflicting. Metric: balanced accuracy of CONFLICT detection at query time.
  Bar: >= 0.9 (flags conflicting, passes consistent). Compare to naive single-answer (silently returns one,
  0% conflict awareness).

## Result — PASS
| metric | value |
|--------|-------|
| conflict detection balanced-acc | **1.00** (TPR 1.00, TNR 1.00) |
| Grace (conflicting) | CONFLICT {Platform, Design} |
| Alice (consistent) | OK {Analytics} |

**VERDICT: PASS.** Query-time conflict handling surfaces inconsistency exactly: gather all same-subject facts
(kind=person), flag if >1 distinct object, return the set. A trustworthy store reports data conflicts at
query time instead of silently returning one of the conflicting answers. Purely symbolic (set logic over
same-subject facts) — geometry resolves the entity, symbols check consistency, same principle as contradiction
detection (GEO-41/52). Added as GeometricReasoner.values_for(). Useful for data-quality auditing of a KB.

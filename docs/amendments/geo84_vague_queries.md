# GEO-84 — Robustness to VAGUE / underspecified natural queries

## Motivation
Real users ask vague, underspecified questions ("that budget thing", "the plumber guy", "when's the tax
thing due"), unlike clean test queries. GEO-84 tests whether semantic matching handles vagueness on the
personal KB — a real robustness question for actual use.

## Pre-registration (locked BEFORE run)
- Personal KB (contacts/tasks/notes, GEO-83). For ~8 facts, write a VAGUE colloquial query and the matching
  fact. Compare retrieval on VAGUE vs CLEAN phrasing of the same query.
- Metric: vague-query hits@1 vs clean-query hits@1. Bar: vague >= 0.7 (handles vagueness) and within 0.2 of
  clean. Honest: if vague << clean, the system needs well-formed queries (a real UX limitation).

## Result — PASS (handles real-user vagueness)
| phrasing | hits@1 |
|----------|--------|
| clean | 1.00 |
| vague/colloquial | **0.88** |
one miss: "the pipe fixing person" -> fix-sink TASK over the plumber CONTACT (cross-type confusion again).

**VERDICT: PASS.** Semantic matching handles VAGUE/colloquial real-user queries (0.88, within 0.12 of clean):
"the teeth doctor" -> dentist, "the legal eagle" -> lawyer, "that money cap thing" -> budget note. The
distributional semantic capability (GEO-69) generalizes to underspecified phrasing — the system does not
require well-formed queries. The single miss is the SAME cross-type confusion (GEO-83): a vague query matching
the wrong fact TYPE, fixed by kind-scoped retrieval (now shipped). So for a personal assistant, real-user
vague queries work well; route to the relevant kind (or use the question's noun/intent) to avoid cross-type
misses. This completes the personal-use validation: the toolkit serves real, messily-phrased personal queries.

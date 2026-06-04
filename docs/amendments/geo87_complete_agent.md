# GEO-87 — Complete integrated agent (LinearRouter + kind-scoping + operators + grounding) end-to-end

## Motivation
All best-practice components are validated and shipped (LinearRouter GEO-86, kind-scoped retrieval GEO-83,
operators, grounding). GEO-87 assembles them into ONE agent — train a kind-router, scope retrieval by routed
kind, apply operators, ground/abstain — and verifies it answers the personal-KB queries (incl. the cross-type
vague ones) end-to-end, the complete usable system.

## Pre-registration (locked BEFORE run)
- Personal KB (contacts/tasks/notes). Train a LinearRouter (kind). Agent: route kind -> kind-scoped retrieve
  -> answer; symbolic count/temporal where applicable; abstain out-of-KB.
- Test set: the GEO-83 + GEO-84 + GEO-85 queries (factoid/semantic/temporal/aggregation/vague/cross-type) +
  out-of-KB.
- Metric: overall accuracy. Bar: >= 0.9 (the complete agent fixes the cross-type miss end-to-end and handles
  the full mixed workload). PASS = the assembled best-practice agent works.

## Result — PARTIAL/NULL (naive integration HURTS — honest finding)
| system | personal-KB accuracy |
|--------|----------------------|
| simple unscoped retrieval (GEO-83/84) | 0.90 / 0.88 |
| "best-practice" agent (router + HARD kind-scoping + grounding) | **0.67** |

**VERDICT: PARTIAL/NULL (important honest lesson).** Assembling the validated components naively made it
WORSE, not better. Root cause: the trained kind-router mis-routes some queries ("kitchen plumbing job" ->
contact instead of task; "money numbers guy" -> wrong kind), and HARD kind-scoping AMPLIFIES those errors — a
wrong routed kind scopes retrieval to the wrong fact set, which then has no match and ABSTAINS (IDK). So
router errors + hard filtering + abstention COMPOUND, dropping accuracy from 0.90 (robust unscoped) to 0.67.

**Lesson (18th self-correction):** more components != better. A fallible router with HARD scoping is worse
than no scoping, because unscoped retrieval is robust to the router's mistakes while hard scoping is not.
Fixes (untested here, recorded honestly): (a) SOFT scoping — boost the routed kind's similarity, don't filter
others out, so a mis-route degrades gracefully; (b) CONFIDENCE-GATE — only scope when the router is confident;
(c) keep it simple — unscoped retrieval + re-ranking was already 0.90. Honest deployment guidance: do NOT
naively stack a router + hard kind-scope; use kind-scoping only when you KNOW the kind (explicit, GEO-83) or
as a soft prior. The simplest robust pipeline (unscoped retrieve + rerank + abstain) often beats the
"best-practice" assembly. NOT retuned — the 0.67 stands as the honest finding.

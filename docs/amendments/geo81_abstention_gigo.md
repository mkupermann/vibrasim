# GEO-81 — Does abstention catch the REALISTIC GIGO scenario (answer absent, similar fact present)?

## Motivation
GEO-80: grounding propagates wrong facts. The deployment guide's safety net is abstention. But the realistic
failure is subtle: the queried answer is ABSENT from the store, yet a SIMILAR fact (same relation, different
entity) is present at high similarity. Does abstention catch this (abstain = safe), or does the similar wrong
fact pass the threshold and get propagated (residual GIGO)? GEO-81 measures the safety net on this case.

## Pre-registration (locked BEFORE run)
- Store has facts for SOME entities; for a set of QUERY entities the answer fact is ABSENT, but same-relation
  facts about OTHER entities are present (high similarity).
- Calibrate abstain_tau on answerable (present) vs clearly-absent (out-of-domain) — the standard calibration.
- Test: query the ABSENT-answer entities. Correct behavior = ABSTAIN. Measure abstain rate.
- Also test the focus-verification guard (GEO-33): does checking the query entity exists in the store catch it?
- Bars: threshold-abstention abstain-rate on absent-answer queries (report); focus-verification abstain-rate
  (expect higher). PASS-as-characterization if focus-verification catches it (>=0.8) where threshold alone may
  not. Honest about the residual risk.

## Result — abstention CATCHES answer-absent (GIGO risk narrowed)
| safeguard | abstain-rate on answer-absent queries |
|-----------|----------------------------------------|
| threshold abstention | 1.00 |
| focus-verification (entity in store?) | 1.00 |
calibrated tau=0.516; "capital of Germany?" -> nearest present fact sim=0.47 < tau -> ABSTAINS.

**VERDICT (corrected, honest, reassuring).** My pre-registration expected threshold abstention to MISS the
answer-absent case; it did NOT — it abstained 1.00. Reason: a query about an ABSENT entity (Germany) has LOW
similarity (0.47) to facts about PRESENT entities (France/Japan/...), because the entity name dominates the
similarity and pushes it below the calibrated threshold. So the realistic GIGO risk is NARROWER than GEO-80
suggested:
- ANSWER ABSENT (queried entity not in store) -> abstention CATCHES it (1.00). Safe.
- WRONG FACT FOR THE RIGHT ENTITY (store contains an incorrect fact for the queried entity — a DATA-QUALITY
  error) -> THIS is the real residual GIGO; grounding propagates it (GEO-80). Caught by contradiction/conflict
  detection (GEO-41/62) at write time and source-verification at read time, NOT by abstention.
**Refined caveat:** the grounding GIGO risk is specifically store DATA QUALITY (wrong facts), not coverage
gaps (abstention handles those). Deployment priority: validate the store's correctness (conflict detection,
provenance) — that, plus abstention for coverage, makes grounding trustworthy. Narrows GEO-80 constructively.

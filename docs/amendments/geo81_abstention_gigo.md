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

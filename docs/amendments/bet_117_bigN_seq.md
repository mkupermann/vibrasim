# BET-117 — Multi-Sequence at Large N: Capacity or Mechanism?

Pre-registered: 2026-05-31. BET-114/116 failed multiple sequences at N=120 (the
capacity edge). Decisive test: does capacity HEADROOM fix it, or is the
transition mechanism itself the wall? Run S=3 and S=5 length-4 sequences at large
N (well above the static capacity needed), with and without context tags.

## Bars
| ID | Criterion | Bar |
|----|-----------|-----|
| T117a | Capacity hypothesis | S=3 sequences at N=300 recalled with min content overlap >= 0.90 |
| T117b | Scaling | S=5 sequences at N=400 recalled with min content overlap >= 0.85 |

PASS (T117a-b) => the multi-sequence limit was CAPACITY: scale N and it works
(good news for the language-scale question). NULL => the transition MECHANISM
interferes even with capacity headroom => language needs a fundamentally stronger
context-dependent predictor, not just more nodes (the honest harder finding).

## RESULT (2026-05-31): NULL — the MECHANISM is the wall, not capacity

S=3 @ N=300: min content overlap 0.741 (up from 0.55 at N=120 — more N helps a
little). S=5 @ N=400: 0.465 (fails). Capacity headroom does NOT fix multi-sequence
recall. T117a x, T117b x.

DECISIVE: the simple Hebbian transition matrix cannot disambiguate multiple
overlapping sequences even with large capacity headroom. Capacity (N) is necessary
but NOT sufficient. This directly answers the language-scale question: you cannot
reach written language by scaling N — the context-dependent SEQUENCE-PREDICTION
mechanism is the binding wall. Written language is the extreme case of overlapping
context-dependent sequences, so a much stronger predictor is required (compositional
/ inferred-context), not merely more nodes. BET-118 attempts the mechanism fix:
hierarchical predictive coding with an INFERRED hidden context layer.

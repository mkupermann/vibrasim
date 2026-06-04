# GEO-80 — The honest downside: does grounding PROPAGATE retrieval errors?

## Motivation
GEO-79: grounding with CORRECT facts helps. The skeptical counterpart: grounding is only as good as retrieval.
If retrieval returns a WRONG fact, does the grounded model confidently give the wrong answer — even on
questions it would get right from memory? GEO-80 quantifies this failure mode (garbage-in-garbage-out), the
honest deployment caveat to GEO-79.

## Pre-registration (locked BEFORE run)
- ~10 COMMON questions the 0.5B model knows from memory (France->Paris, Japan->Tokyo, etc.).
- Three conditions: (a) BARE (memory), (b) GROUNDED-CORRECT (right fact in context), (c) GROUNDED-WRONG
  (a WRONG fact in context, e.g. "The capital of France is Lyon").
- Metric: accuracy vs the TRUE answer. Expectation: bare high, grounded-correct high, grounded-WRONG LOW
  (model follows the wrong context). Bars (descriptive): if grounded-wrong << bare, grounding propagates
  retrieval errors — the honest GIGO caveat. Report all three.

## Result — CONFIRMED (grounding is double-edged)
| condition | true-accuracy |
|-----------|---------------|
| (a) bare (memory) | 0.90 |
| (b) grounded-correct | 1.00 |
| (c) grounded-WRONG | **0.00** (followed wrong fact 1.00) |

**VERDICT: CONFIRMED (honest GIGO).** Grounding with a WRONG retrieved fact collapses accuracy from 0.90
(bare) to 0.00 — the model follows the wrong context 100% of the time, OVERRIDING its own correct memory.
Grounding is DOUBLE-EDGED: +0.83 with correct retrieval (GEO-79), -0.90 with wrong retrieval (GEO-80).

## Balanced grounding verdict (GEO-79 + GEO-80)
Grounding's value is ENTIRELY contingent on retrieval quality:
- retrieval RIGHT -> grounding makes a weak model reliable (0.17 -> 1.00).
- retrieval WRONG -> grounding makes a correct model confidently wrong (0.90 -> 0.00).
So the system amplifies retrieval — for better AND worse. Deployment guidance (honest): (1) invest in
retrieval quality (re-ranking GEO-40b/56b, entity-resolution GEO-44, better embeddings GEO-36); (2) ABSTAIN
on low-confidence retrieval (GEO-23) — the essential safety net, since a wrong-but-confident retrieval yields
a wrong-but-confident answer; (3) prefer EXTRACTIVE (return the fact) over generative when the user can verify
the source. The honest net: grounding is the system's biggest strength AND its biggest risk; retrieval quality
+ abstention are what make it trustworthy rather than confidently wrong. This balances the GEO-79 positive.

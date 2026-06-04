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

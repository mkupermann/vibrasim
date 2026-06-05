# JEP-351 — Mapping the wall: genuinely complex real encyclopedia prose

## Motivation
JEP-350: 100% on CLEAR factual sentences. The honest question is where Half-1 ENDS. Feed a genuinely complex real
encyclopedia paragraph (passive voice, "such as" lists, comparatives, appositives, dates, abstract relations) — NOT
tuned to our normalizers — and measure coverage honestly, categorizing which forms fail. This maps the boundary the
project has named since the start (messy real writing). No transformer.

## Method
Read a ~8-sentence real Wikipedia-style intro (about the dog) with natural complexity; measure parse coverage and
list each sentence's outcome + the construction that defeated it.

## Pre-registered PREDICTION (this is a characterization, not a tuned threshold)
- I predict coverage will be **LOW — roughly 0.15–0.40** on genuinely complex prose (vs 1.0 on clean prose),
  because passive voice ("were domesticated"), "such as" lists, comparatives ("vary widely"), and abstract verbs
  ("led to", "attuned to") are NOT declarative is-a/property forms our engine+normalizer handle.
- **J351a (honesty bar):** report the exact coverage and a per-sentence failed-form categorization, both seeds. The
  experiment PASSES as an honest boundary characterization regardless of the number; the FINDING is the number +
  the named failing constructions (which would each need a special-data or rule, or relaxing the no-LLM rule).

Predicted most-likely surprise: a couple of sentences DO parse (the few declarative ones), so coverage isn't zero —
that's expected and honest.

## Result (seeds 0, 7): **PASS** (honest boundary mapped; PREDICTION HIT)
- Coverage on genuinely complex real prose = **0.25 (2/8)**, both seeds — squarely in the predicted 0.15–0.40 range
  (**prediction HIT**). The 2 that parsed are the clean "A dog is a mammal." and the plural "Dogs are carnivores."
- The 6 that FAILED, by construction (the documented wall):
  1. passive/appositive — "is a domesticated descendant of the wolf"
  2. passive — "were domesticated by humans"
  3. passive perfect — "has been bred over millennia"
  4. abstract causal — "has led dogs to be attuned to human behavior"
  5. comparative/list — "vary widely in shape, size, and color"
  6. such-as list — "perform many roles, such as hunting, herding, and pulling loads"

## Verdict: **PASS** (the finding is the boundary)
Honest map: on CLEAR factual prose the brain reads ~100% (JEP-350); on genuinely complex REAL encyclopedia prose it
reads **~25%**, and the failing constructions are exactly the "messy real writing" wall the project named from the
start. Some are addressable with more rules (such-as lists → multiple is-a; comparatives → properties); passive
voice and abstract causal genuinely need either much more hand-built parsing, the world-knowledge a transformer
absorbs, or relaxing the no-LLM rule. This experiment **confirms the honest prediction** given to Michael: Half-1
works for clear text, not arbitrary real text. No transformer.


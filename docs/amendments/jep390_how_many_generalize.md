# JEP-390 — Generalize how_many to any counted part (not just legs)

## Motivation
JEP-389 found "A car has four wheels" stores (car, has_wheels, 4) but "how many wheels does a car have?" returns
nothing: `how_many` is hardcoded to read `has_legs`, and the parser ignores the part name. Same stored-but-unreachable
class as the part-of query gap. Fix: parse the part name and query `has_<part>`, defaulting to legs for back-compat.
No transformer.

## Method
- `BrainQuery.how_many(x, part="legs")` queries `has_<part>` (inherited via ancestors).
- The "how many <part> does <X> have?" parser captures <part> and passes it.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: any counted part becomes queryable; legs still work; JEP-389 Q&A rises (the wheels gap closes; the
adjectival-subject causal gap remains, so Q&A → ~0.90).

- **J390a (any part):** "A car has four wheels" → "how many wheels does a car have?" = 4; "A dog has four legs" →
  "how many legs does a dog have?" = 4 (regression), both seeds (0, 7).
- **J390b (JEP-389 Q&A rises):** re-running JEP-389, Q&A accuracy ≥0.90 (the how_many gap closed), both seeds.
- **J390c (no regression):** "does a dog have legs?" still works; `pytest -m "not slow" tests/test_conversation.py`
  passes.

If generalizing how_many breaks the legs default, report it. Predicted clean. Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT)
- **J390a (any part): PASS** — "how many wheels does a car have?" → 4; "how many legs does a dog have?" → 4; "does a
  dog have legs?" → yes (default preserved). Both seeds.
- **J390b (JEP-389 Q&A rises): PASS** — re-running JEP-389, Q&A accuracy **0.80 → 0.90** (the wheels count is now
  queryable); the only remaining miss is "what causes accidents?" (adjective+noun subject "Worn brakes", a separate
  documented gap). Both seeds.
- **J390c (no regression): PASS** — `tests/test_conversation.py` **10 passed**. Both seeds.

## Verdict: **PASS — any counted part is now queryable**
Generalizing `how_many(x, part)` to read `has_<part>` (defaulting to legs) and capturing the part name in the parser
closes another stored-but-unreachable gap: counts like "how many wheels does a car have?" are now answered, while legs
queries are unchanged. JEP-389 relational Q&A rises to 0.90; the lone residual is adjective+noun relational subjects
("Worn brakes cause accidents"), logged as a separate, lower-frequency gap. Established rule-based query routing; no
transformer.

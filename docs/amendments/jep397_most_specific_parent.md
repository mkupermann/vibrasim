# JEP-397 — Most-specific parent selection (so consolidation doesn't flatten "what is X" / describe)

## Motivation
JEP-396 found that after closure consolidation, all ancestor is-a edges are direct, so `query(x,"isa")` returns an
arbitrary ancestor — "tell me about a rose" / "what is a rose?" can answer "plant" instead of the most-specific
"flower". Fix: among the materialized ancestor candidates, select the MOST SPECIFIC (the one deepest in the hierarchy,
i.e. with the most ancestors of its own). Used by `describe` and "what is X". No transformer.

## Method
Add `BrainQuery._most_specific_parent(x)`: from `query_all(x,"isa")` candidates, return the one with the most ancestors
(deepest), which is the most specific. Use it in `describe` and the "what is X" parser.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: most-specific parent is chosen; deeper chains and single-parent cases unaffected.

- **J397a (specific over general):** after "A rose is a flower. A flower is a plant." → "what is a rose?" → flower (not
  plant); `describe(rose)` says "a rose is a flower", both seeds (0, 7).
- **J397b (deep chain):** after "A poodle is a dog. A dog is a mammal. A mammal is an animal." → "what is a poodle?" →
  dog (most specific), both seeds.
- **J397c (no regression):** a single-parent concept still answers correctly; is_a multi-hop still works (JEP-378
  reliability intact via consolidate); `pytest -m "not slow" tests/test_conversation.py` passes.

If most-specific selection misfires (e.g. ties), report it. Predicted clean. Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT)
- **J397a (specific over general): PASS** — "what is a rose?" → **flower** (not plant); "tell me about a rose" → "a
  rose is a flower." Both seeds.
- **J397b (deep chain): PASS** — "what is a poodle?" → **dog** (most specific of dog/mammal/animal). Both seeds.
- **J397c (no regression): PASS** — single-parent "what is a car?" → vehicle; multi-hop "is a poodle an animal?" → yes
  (consolidation/reasoning intact); `tests/test_conversation.py` **10 passed**. Both seeds.

## Verdict: **PASS — discussion is informative again; consolidation no longer flattens the named parent**
`_most_specific_parent(x)` selects the deepest materialized ancestor (most ancestors of its own), so `describe` and
"what is X" name the most-specific class ("a rose is a flower", "a poodle is a dog") even though closure consolidation
made all ancestors direct edges — while multi-hop reasoning and single-parent cases are unaffected. This closes the
JEP-396 quality regression: the substrate's discussion of what it read is both correct AND specific. Established
hierarchy selection; no transformer.

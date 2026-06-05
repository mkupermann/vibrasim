# JEP-330 — Numeric attribute reasoning with inheritance (how many legs? more than?)

## Motivation
The suite covers relations but not NUMERIC attributes. Store quantities as (entity, attr, count-symbol) facts and
answer "how many legs does a poodle have?" via is-a inheritance (poodle→dog→4), and "does a dog have more legs than
a bird?" by interpreting the retrieved count symbols as numbers. Reuses the inheritance climb (JEP-301); the count
is just a value symbol + a numeric decode at the end. No transformer.

## Method
Facts (dog, has_legs, "4"), (bird, has_legs, "2"), … with is-a taxonomy. `how_many(x, attr)` = climb x's is-a
ancestors (most specific first), return the first attr value found; decode to int. `compare(x, y, attr)` = sign of
how_many(x)−how_many(y).

## Pre-registered bars (BEFORE the run)
- **J330a (inherited quantity):** `how_many` matches ground truth incl. INHERITED (poodle→dog→4, sparrow→bird→2)
  and a specific override (a tripod_dog with explicit 3 beats dog's 4) ≥ 0.95, both seeds (0, 7).
- **J330b (numeric comparison):** `compare(dog, bird, has_legs)` and a few others match the true ordering, ≥ 0.95.
- **J330c (persists):** answers identical after reload.

Predicted most-likely failure: count symbols ("2","4") are near-orthogonal atoms like any symbol, so retrieval is
fine; the risk is the OVERRIDE (specific count beating inherited) needing most-specific-first order — same as
JEP-301/305. If J330a misses on the override, report the ancestor-walk order.

## Result (seeds 0, 7): **PASS**
- **J330a:** `how_many` = **1.0** — poodle→4 (inherited from dog), sparrow→2 (from bird), spider→8 (from arachnid),
  and **tripod_dog→3 (explicit override beats dog's inherited 4)**, both seeds. **PASS.**
- **J330b:** numeric comparison = **1.0** — dog>bird, bird<spider, poodle>tripod_dog, sparrow<dog, both seeds.
  **PASS.**
- **J330c:** identical after reload. **PASS.**

## Verdict: **PASS**
The durable store answers numeric-attribute questions ("how many legs does a poodle have?" → 4) by is-a
inheritance with most-specific-override (a 3-legged dog beats the inherited 4), and numeric comparison ("more legs
than?") by decoding the retrieved count symbols. Quantities are ordinary value atoms + a numeric decode at the
readout — no special machinery. Quantity/number reasoning now joins the suite (is-a, part-of, causal, property,
open, inheritance, DAG, negation, abduction, contradiction, symmetric, transitive, analogy, temporal, numeric). No
transformer.


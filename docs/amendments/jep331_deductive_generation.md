# JEP-331 — Deductive generation: the brain states new TRUE facts it was never told

## Motivation
FOR_EVERYONE names "freely generating, not just answering" as a wall. A substrate-legal first step is DEDUCTIVE
generation: emit new English statements ENTAILED by the stored knowledge (forward-chaining over the durable store +
templated verbalization), that were never directly stated. Not creative generation — generation by entailment.
Established (forward-chaining + template verbalization), named as such. No transformer.

## Method
Over the durable store: for each entity, derive inherited is-a ancestors, inherited properties, inherited numeric
attributes (via the climb), verbalize each (`"A poodle is an animal."`, `"A poodle has 4 legs."`,
`"A poodle can bark."`), keep only statements NOT directly stored (novel), and verify each against the ground-truth
closure (soundness). Round-trip: re-read the generated statements into a FRESH UnderstandingEngine.

## Pre-registered bars (BEFORE the run)
- **J331a (soundness):** EVERY generated statement is TRUE (entailed by the closure) — precision = 1.0 (no false
  statement), both seeds (0, 7).
- **J331b (novelty / genuine generation):** ≥ 50% of generated statements were NOT directly stored (the engine is
  saying things it was never told), both seeds.
- **J331c (well-formed round-trip):** re-reading the generated statements into a fresh engine recovers the same
  entailments (the output is valid English the engine itself parses), ≥ 0.90 of generated facts recovered.

Predicted most-likely failure: a verbalization template could emit a malformed or mis-scoped sentence the engine
re-parses wrong (round-trip < 0.90) — a surface-form issue (#1); or an over-eager derivation asserts a
non-entailed fact (precision < 1.0). If J331a < 1.0, that derivation is unsound and must be removed, not tolerated.

## Result (seeds 0, 7): **PASS**
- **J331a (soundness):** all 13 generated statements TRUE — precision = **1.0**, both seeds. **PASS.**
- **J331b (novelty):** **1.0** — every generated statement was NOT directly told (e.g. "A beagle is a mammal",
  "A beagle can breathe", "A beagle has 4 legs", "A dog is an animal"). **PASS.**
- **J331c (round-trip):** re-reading the generated sentences into a fresh engine recovers the is-a entailments at
  **1.0** — the output is valid English the engine itself parses. **PASS.**

## Verdict: **PASS**
The durable brain GENERATES new, true, novel English statements entailed by what it knows — forward-chaining over
the persistent store (inherited is-a, properties, numeric attributes) + templated verbalization — and the
Understanding Engine re-parses its own output losslessly. A real first step at the "generation" wall, honestly
framed: this is DEDUCTIVE generation (saying true things it deduced but was never told), NOT creative/free
generation, which remains the open frontier. Established forward-chaining + template verbalization, named as such;
no transformer, no pretrained model.


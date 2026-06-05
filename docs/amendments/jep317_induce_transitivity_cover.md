# JEP-317 — Induce transitivity from a COVER-only store via a few labeled examples (closes JEP-316 scope gap)

## Motivation
JEP-316 detected transitivity only when the closure was materialized (the signal was in the facts). The honest
harder case: a relation stored as its COVER (a→b→c, NOT a→c). Pattern statistics can't see it. Use a few SUPERVISED
labeled examples ("is a→c true?") to induce a per-relation transitive flag, then let the gated multi-hop CLIMB do
the actual inference over the cover. Established supervised rule induction, named as such. No transformer.

## Method
Store transitive relations as cover only; non-transitive as-is. For each relation, take K=3 labeled composed-pair
examples (a→…→c with the true holds/not label). Induce: relation is transitive if the labeled composed pairs are
TRUE at rate ≥ 0.7. For a transitive-flagged relation, answer held-out queries by the climb over the cover; for
others, direct membership. Score vs ground-truth closure.

## Pre-registered bars (BEFORE the run)
- **J317a (induce the flag):** correctly flag transitive vs non-transitive relations from K=3 labeled examples
  each, ≥ 0.90 over the relation set, both seeds (0, 7).
- **J317b (genuine inference over the cover):** for transitive-flagged relations, the climb answers HELD-OUT
  composed queries (not in the labeled set, not materialized) vs closure ≥ 0.90, both seeds.
- **J317c (persists):** flags + held-out answers identical after reload, both seeds.

Predicted most-likely failure: deep cover chains (≥4) could drop a held-out positive below the gate (JEP-307
routing should hold per-hop), or 3 labeled examples could be too few to separate a relation with occasional
coincidental composed pairs. If J317a flips a class, report the relation + its labeled-example rate; if J317b
misses on depth, report the max reliable cover-depth — neither tuned.

## Result (seeds 0, 7): **PASS** (after a diagnosed ground-truth bug)
- **First cut:** flag-classify = **0.5** (ALL relations flagged transitive). Root cause = MY experiment's ground
  truth used `closure()` for every relation, which makes a non-transitive relation's composed pair look true
  ("cat→fish→algae ⇒ cat eats algae"). The true extension of a non-transitive relation is its DIRECT edges only.
  (Calibration lesson #3: the ground truth must discriminate the property it scores.)
- **Fixed ground truth** (transitive → closure; non-transitive → direct edges):
  - **J317a:** flag-classify = **1.0** — ancestor_of/located_in/bigger_than → transitive; eats/likes/parent_of →
    not, both seeds. **PASS.**
  - **J317b:** held-out composed queries (not labeled, not materialized) via climb-if-flagged-else-direct vs true
    extension = **1.0**, incl. a 4-hop cover inference (ancestor a→e). **PASS.**
  - **J317c:** persists. **PASS.**

## Verdict: **PASS**
Transitivity is induced from K=3 labeled examples on a COVER-only store, and the gated climb (JEP-307 routing) then
does genuine multi-hop inference the facts never materialized — while non-transitive relations are correctly held
to direct edges. Closes the JEP-316 scope gap (no longer needs the closure pre-materialized). Honest note: the fix
was to my ground-truth definition, not the substrate; the climb mechanism was correct from the first run (J317b's
inference worked even under the wrong labels). Established supervised rule induction + closure inference, named.


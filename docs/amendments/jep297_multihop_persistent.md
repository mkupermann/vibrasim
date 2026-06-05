# JEP-297 — Multi-hop reasoning over the persistent substrate memory (memory → inference)

## Motivation
JEP-295/296 gave a durable, growing key→value store. Michael's goal is a brain that *understands*, not just recalls.
This shows the SAME persistent VSA store supports **transitive inference at recall time**: climb an is-a chain by
iterated unbind (poodle→dog→mammal→animal→organism) to answer a question never stored directly — and have the
answer survive close+reopen. Climbing needs an "is there still a parent?" gate — exactly the rejection-margin edge
left open in JEP-296 — so this also closes that with a pre-registered, calibration-derived threshold (no tuning).

## Method
Facts = (child, "isa", parent) in a `SubstrateMemory`. `is_a(x, y)`: from x, repeatedly `query(current,"isa")`;
accept the returned parent only if its cleanup similarity ≥ GATE; stop when no parent clears the gate or y is found
(cap at chain length). GATE is set ONCE from held-out calibration facts as the midpoint between the mean taught-edge
similarity and the mean untaught (random-entity) similarity — derived from data, fixed before scoring the test.

## Pre-registered bars (BEFORE the run)
- **J297a (multi-hop correct):** with a depth-5 chain + distractor branches, `is_a(poodle, organism)` = True
  (5 hops, never stored directly), `is_a(poodle, fish)` = False, a 1-hop `is_a(dog, mammal)` = True, and a
  non-fact `is_a(rock, mammal)` = False — ALL four correct, both seeds (0, 7).
- **J297b (persists):** save → load into a FRESH object → the four answers are identical. Both seeds.
- **J297c (gate terminates cleanly):** climbing always halts (no infinite loop) and the top of the chain
  (`organism`) returns no further parent — i.e. the gate rejects the random continuation.

Predicted most-likely failure: accumulated per-hop similarity decay makes a true deep parent fall below GATE
(false "no"), or crosstalk makes a wrong parent clear GATE (false hop). If J297a fails on depth, report the max
reliable hop-depth as the honest finding rather than moving GATE.

## Result (seeds 0, 7): **NULL** — direction-ambiguous binding
- `is_a(poodle, organism)` = **False** (want True); only the 1-hop `is_a(dog, mammal)` = True. J297a/b/c all False.
- **Root cause (probed, confirmed):** plain Hadamard binding makes is-a edges **undirected**. Because `bind` is
  multiplication and self-inverse, a fact `bind(bind(child, ROLE), parent)` is recovered by the key `child*ROLE`
  → parent, BUT is *also* triggered by `parent*ROLE` → child. So a query at an interior node returns BOTH its
  parents and its children, and `argmax` often picks a child:
  - `query(organism, isa)` → **animal** (its child; organism has no parent) — sim 0.205
  - `query(animal, isa)` → **bird** (a child) instead of organism
  The chain climb therefore wanders sideways/down and never reaches `organism`.

## Verdict: **NULL** (valid finding, not a retry)
Transitive inference needs **directed** edges; commutative self-inverse binding cannot represent direction. The
established fix is a non-commutative role operator — **permutation-protected binding** (Kanerva): store the parent
as `permute(parent)` so `child*permute(parent)` is recovered forward but a backward probe yields a *permuted*
(non-clean) vector that the cleanup rejects. Pre-registered as **JEP-298**. Honest: the JEP-294/295/296 key→value
results are unaffected (those are single-step, direction is never queried both ways); only multi-hop climbing
exposed the symmetry.


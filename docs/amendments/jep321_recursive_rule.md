# JEP-321 — Inducing a RECURSIVE rule: ancestor = transitive closure of parent

## Motivation
JEP-319 induced fixed 2-relation compositions. The harder ILP case is a RECURSIVE rule: ancestor_of(a,c) :-
parent_of(a,c); ancestor_of(a,c) :- parent_of(a,b), ancestor_of(b,c) — i.e. ancestor is the transitive CLOSURE of
parent, of unbounded depth. Induce which base relation's closure equals a target from examples, then answer
held-out target queries by the base climb (genuine recursion over the store). Established ILP closure induction,
named as such. No transformer.

## Method
Bases stored (parent_of as a tree, sibling_of as a distractor). For target T with K labeled (a,c) examples and a
gate, closure-coverage(B) = rate over examples that the gated climb on B reaches c from a. Induce T = closure(B*)
for the base B* with coverage ≥ 0.8 (and clearly above the runner-up). Apply: T(a,c) ⇔ climb_B*(a,c).

## Pre-registered bars (BEFORE the run)
- **J321a (induce the recursive base):** ancestor_of → parent_of (not sibling_of); a scrambled target → no base;
  both seeds (0, 7).
- **J321b (apply held-out, incl. deep):** held-out ancestor queries (incl. ≥4-hop, never labeled/stored) via the
  parent climb vs ground-truth closure ≥ 0.90, both seeds.
- **J321c (persists):** induction + answers identical after reload, both seeds.

Predicted most-likely failure: deep climbs (≥5) could drop a positive below the routed gate (recall miss) — JEP-307
routing should hold; if J321b misses on depth, report the max reliable depth, not a tuned gate. sibling_of closure
could coincidentally cover a few ancestor examples (siblings share parents) inflating its coverage; if it ties
parent_of, report the separability.

## Result (seeds 0, 7): **PASS** (after a diagnosed method bug)
- **First cut:** NULL — base=None, held-out 0.0, even g0→g5 climb False. Root cause = MY climb used single-best
  `query` per hop on a BRANCHING parent tree (g0 has children g1 AND h1), so it followed one branch and missed the
  other — not a substrate failure. Fix = BFS over `query_all` (the JEP-303 set-valued mechanism).
- **Fixed:**
  - **J321a:** induced ancestor_of = closure(**parent_of**) (not sibling_of); scrambled target → no base. **PASS.**
  - **J321b:** held-out ancestor queries incl. **5-hop (g0→g5)** via the parent BFS vs closure = **1.0**. **PASS.**
  - **J321c:** persists. **PASS.**

## Verdict: **PASS**
The substrate induces a RECURSIVE rule — that a relation is the transitive CLOSURE of a base of unbounded depth —
from a few examples, and answers held-out deep queries by the recursive base climb. With JEP-316/317/318/319 the
system now learns symmetry, transitivity, inverses, fixed composition, AND recursive-closure rules from data.
Honest lesson (reinforces calibration): a single-best climb fails on branching structure; closure reasoning needs
set-valued BFS (`query_all`). The bug was the experiment's traversal, not the substrate.

